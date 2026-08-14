module.exports = {
  apps: [
    {
      name: 'school-backend',
      script: '/var/www/school-site-updated-backend/venv/bin/python',
      args: '-m uvicorn main:app --host 127.0.0.1 --port 8000 --workers 2',
      interpreter: 'none',
      cwd: '/var/www/school-site-updated-backend',
      watch: false,
      autorestart: true,
      restart_delay: 3000,
      env: {
        PYTHONPATH: '/var/www/school-site-updated-backend',
      },
    },
  ],
};
