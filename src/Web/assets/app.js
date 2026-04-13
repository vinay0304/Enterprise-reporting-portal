const API_BASE = 'http://localhost:5000/api'; // Adjust to your local API URL

const App = {
    token: localStorage.getItem('token'),

    async fetch(url, options = {}) {
        if (!this.token && !url.includes('/auth/login')) {
            // In a real app, redirect to login
            console.warn("No token found. Attempting auto-login for demo...");
            await this.login('admin', 'password123');
        }

        const headers = {
            'Content-Type': 'application/json',
            ...(this.token && { 'Authorization': `Bearer ${this.token}` }),
            ...options.headers
        };

        const response = await fetch(`${API_BASE}${url}`, { ...options, headers });
        if (response.status === 401) {
            localStorage.removeItem('token');
            // Re-login for demo
            await this.login('admin', 'password123');
            return this.fetch(url, options);
        }
        return response;
    },

    async login(username, password) {
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        const data = await response.json();
        if (data.token) {
            this.token = data.token;
            localStorage.setItem('token', data.token);
        }
    },

    async loadDashboard() {
        try {
            const res = await this.fetch('/data/status');
            const data = await res.json();
            
            document.getElementById('processed-count').textContent = data.totalRecordsProcessed || 0;
            document.getElementById('error-count').textContent = data.activeErrorsCount || 0;
            document.getElementById('today-count').textContent = data.recordsReceivedToday || 0;
            document.getElementById('last-run').textContent = data.lastReportRunAt 
                ? new Date(data.lastReportRunAt).toLocaleString() 
                : 'Never';
        } catch (e) {
            console.error("Dashboard error:", e);
        }
    },

    async loadReports() {
        try {
            const res = await this.fetch('/reports');
            const reports = await res.json();
            const body = document.getElementById('reports-body');
            body.innerHTML = '';

            reports.forEach(r => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>#${r.runId}</td>
                    <td>${r.reportName}</td>
                    <td><span class="badge ${this.getStatusBadgeClass(r.status)}">${r.status}</span></td>
                    <td>${new Date(r.startedAt).toLocaleString()}</td>
                    <td>${r.completedAt ? new Date(r.completedAt).toLocaleString() : '-'}</td>
                    <td>
                        ${r.status === 'Completed' ? `<button onclick="App.downloadReport(${r.runId})" class="btn btn-primary" style="padding: 0.3rem 0.6rem; font-size: 0.75rem;">Download</button>` : ''}
                    </td>
                `;
                body.appendChild(tr);
            });
        } catch (e) {
            console.error("Reports error:", e);
        }
    },

    async runNewReport() {
        const reportName = prompt("Enter Report Name:", "System Sales Report");
        if (!reportName) return;

        try {
            await this.fetch('/reports/run', {
                method: 'POST',
                body: JSON.stringify({ reportName, parameters: "{}" })
            });
            this.loadReports();
        } catch (e) {
            alert("Failed to trigger report.");
        }
    },

    async downloadReport(runId) {
        try {
            const res = await fetch(`${API_BASE}/reports/${runId}/download`, {
                headers: { 'Authorization': `Bearer ${this.token}` }
            });
            const blob = await res.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `Report_${runId}.pdf`;
            document.body.appendChild(a);
            a.click();
            a.remove();
        } catch (e) {
            alert("Download failed.");
        }
    },

    getStatusBadgeClass(status) {
        switch(status) {
            case 'Completed': return 'badge-success';
            case 'Failed': return 'badge-error';
            case 'Running': return 'badge-warning';
            default: return '';
        }
    },

    async handleFileUpload(files) {
        if (!files.length) return;
        const file = files[0];
        
        const statusDiv = document.getElementById('upload-status');
        const filenameSpan = document.getElementById('upload-filename');
        const percentSpan = document.getElementById('upload-percent');
        const progressBar = document.getElementById('upload-progress-bar');

        statusDiv.style.display = 'block';
        filenameSpan.textContent = file.name;

        const formData = new FormData();
        formData.append('file', file);
        formData.append('sourceSystem', 'WebPortal');

        // Note: fetch doesn't support progress natively easily, so we use logic or just simulate
        // For a true progress bar, we'd use XMLHttpRequest
        try {
            const xhr = new XMLHttpRequest();
            xhr.open('POST', `${API_BASE}/data/upload?sourceSystem=WebPortal`);
            xhr.setRequestHeader('Authorization', `Bearer ${this.token}`);
            
            xhr.upload.onprogress = (e) => {
                if (e.lengthComputable) {
                    const percent = Math.round((e.loaded / e.total) * 100);
                    percentSpan.textContent = `${percent}%`;
                    progressBar.style.width = `${percent}%`;
                }
            };

            xhr.onload = () => {
                if (xhr.status === 200) {
                    alert("Upload successful! Ingestion will start shortly.");
                } else {
                    alert("Upload failed.");
                }
                statusDiv.style.display = 'none';
            };

            xhr.send(formData);
        } catch (e) {
            alert("Upload error.");
        }
    },

    async loadErrors(page = 1) {
        try {
            const res = await this.fetch(`/errors?page=${page}&pageSize=10`);
            const errors = await res.json();
            const body = document.getElementById('errors-body');
            body.innerHTML = '';

            errors.forEach(err => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${err.errorId}</td>
                    <td>${err.sourceFile}</td>
                    <td style="color: var(--warning)">${err.errorType}</td>
                    <td style="font-size: 0.8rem; max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${err.errorMessage}">${err.errorMessage}</td>
                    <td>${new Date(err.createdAt).toLocaleDateString()}</td>
                    <td><span class="badge badge-error">${err.isResolved ? 'Resolved' : 'Active'}</span></td>
                `;
                body.appendChild(tr);
            });
        } catch (e) {
            console.error("Errors error:", e);
        }
    }
};

window.App = App;
