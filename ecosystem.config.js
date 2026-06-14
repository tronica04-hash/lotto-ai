module.exports = {
  apps: [{
    name: "lottoai-production",
    script: "orchestrator.py",
    interpreter: "python",
    cwd: "D:\\lotto-ai",
    max_restarts: 0,
    autorestart: false,
    watch: false,
    max_memory_restart: "500M",
    log_date_format: "YYYY-MM-DD HH:mm:ss",
    error_file: "D:\\lotto-ai\\logs\\pm2-error.log",
    out_file: "D:\\lotto-ai\\logs\\pm2-out.log",
  }]
}
