const { createApp } = Vue;

createApp({
  data() {
    return {
      resumes: [], selectedResume: null, sessionId: '',
      messages: [], allJobs: [], draft: '',
      showJobsModal: false,
      resumeModal: null,
      jobModal: null,
      loadingResumes: false, loadingChat: false, loadingAllJobs: false,
      resumeError: '', chatError: ''
    };
  },
  computed: {
    canSend() {
      return Boolean(this.sessionId && this.draft.trim() && !this.loadingChat);
    }
  },
  mounted() {
    this.loadResumes();
    this.loadAllJobs();
  },
  methods: {
    async loadResumes() {
      this.loadingResumes = true; this.resumeError = '';
      try {
        const r = await fetch('/api/resumes/');
        if (!r.ok) throw new Error('简历加载失败');
        this.resumes = await r.json();
      } catch (e) { this.resumeError = e.message; }
      finally { this.loadingResumes = false; }
    },
    async loadAllJobs() {
      this.loadingAllJobs = true;
      try {
        const r = await fetch('/api/jobs/');
        if (!r.ok) throw new Error('岗位加载失败');
        this.allJobs = await r.json();
      } catch (e) { console.error(e); }
      finally { this.loadingAllJobs = false; }
    },
    async selectResume(resume) {
      if (this.loadingChat) return;
      this.resumeError = ''; this.chatError = '';
      this.selectedResume = resume; this.sessionId = ''; this.messages = [];
      try {
        const r = await fetch('/api/chat/sessions', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ resume_id: resume.id })
        });
        const data = await r.json();
        if (!r.ok) throw new Error(data.detail || '会话创建失败');
        this.sessionId = data.session_id;
      } catch (e) { this.selectedResume = null; this.resumeError = e.message; }
    },
    useSuggestion(text) {
      if (!this.sessionId) return;
      this.draft = text;
      this.$nextTick(() => this.sendMessage());
    },
    async sendMessage() {
      if (!this.canSend) return;
      const content = this.draft.trim();
      this.messages.push({ role: 'user', content, jobs: [] });
      this.draft = ''; this.loadingChat = true; this.chatError = '';
      this.$nextTick(this.scrollMessages);

      // 预先插入一条空的 AI 消息，通过索引修改保证响应式更新
      this.messages.push({ role: 'assistant', content: '', jobs: [] });
      const aiIndex = this.messages.length - 1;

      try {
        const res = await fetch('/api/chat/stream', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ session_id: this.sessionId, message: content })
        });
        if (!res.ok) {
          const data = await res.json();
          throw new Error(data.detail || '发送失败');
        }

        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });

          const parts = buffer.split('\n\n');
          buffer = parts.pop();

          for (const part of parts) {
            const line = part.trim();
            if (!line.startsWith('data: ')) continue;
            let event;
            try { event = JSON.parse(line.slice(6)); } catch { continue; }

            if (event.type === 'token') {
              this.messages[aiIndex] = {
                ...this.messages[aiIndex],
                content: this.messages[aiIndex].content + event.content
              };
              this.$nextTick(this.scrollMessages);
            } else if (event.type === 'jobs') {
              this.messages[aiIndex] = {
                ...this.messages[aiIndex],
                jobs: event.jobs || []
              };
              this.$nextTick(this.scrollMessages);
            } else if (event.type === 'error') {
              this.chatError = event.message;
              if (!this.messages[aiIndex].content) {
                this.messages[aiIndex] = {
                  ...this.messages[aiIndex],
                  content: '抱歉，当前暂时无法完成回复，请稍后再试。'
                };
              }
            }
          }
        }
      } catch (e) {
        this.chatError = e.message;
        if (!this.messages[aiIndex].content) {
          this.messages[aiIndex] = {
            ...this.messages[aiIndex],
            content: '抱歉，当前暂时无法完成回复，请稍后再试。'
          };
        }
      } finally {
        this.loadingChat = false;
        this.$nextTick(this.scrollMessages);
      }
    },
    viewJob(job) {
      this.jobModal = job;
    },
    viewResume(resume) {
      this.resumeModal = resume;
    },
    scrollMessages() {
      const el = this.$refs.messageList;
      if (el) el.scrollTop = el.scrollHeight;
    }
  }
}).mount('#app');
