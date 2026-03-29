const API_BASE = '/api/camera_connection';

let currentCameraType = 'usb';
let sessionId = null;
let refreshInterval = null;

document.addEventListener('DOMContentLoaded', function() {
    const currentPath = window.location.pathname;
    
    if (currentPath.includes('bind')) {
        initBindPage();
    } else if (currentPath.includes('monitor')) {
        initMonitorPage();
    }
});

function initBindPage() {
    const typeOptions = document.querySelectorAll('.type-option');
    const usbForm = document.getElementById('usbForm');
    const rtspForm = document.getElementById('rtspForm');
    const bindButton = document.getElementById('bindButton');
    const errorMessage = document.getElementById('errorMessage');
    const successMessage = document.getElementById('successMessage');
    const loading = document.getElementById('loading');
    
    typeOptions.forEach(option => {
        option.addEventListener('click', function() {
            typeOptions.forEach(opt => opt.classList.remove('active'));
            this.classList.add('active');
            currentCameraType = this.dataset.type;
            
            if (currentCameraType === 'usb') {
                usbForm.classList.remove('hidden');
                rtspForm.classList.add('hidden');
            } else {
                usbForm.classList.add('hidden');
                rtspForm.classList.remove('hidden');
            }
        });
    });
    
    bindButton.addEventListener('click', async function() {
        const cameraName = document.getElementById('cameraName').value.trim();
        
        if (!cameraName) {
            showError('请输入摄像头名称');
            return;
        }
        
        hideMessages();
        bindButton.disabled = true;
        loading.style.display = 'block';
        
        try {
            const data = {
                camera_type: currentCameraType,
                camera_name: cameraName
            };
            
            if (currentCameraType === 'usb') {
                data.device_index = document.getElementById('deviceIndex').value;
            } else {
                data.ip = document.getElementById('ip').value.trim();
                data.port = document.getElementById('port').value;
                data.username = document.getElementById('username').value.trim();
                data.password = document.getElementById('password').value;
                data.brand = document.getElementById('brand').value;
                data.model = document.getElementById('model').value.trim();
            }
            
            const response = await fetch(`${API_BASE}/bind`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.success) {
                sessionId = result.data.session_id;
                localStorage.setItem('camera_session_id', sessionId);
                localStorage.setItem('camera_name', result.data.camera_name);
                
                showSuccess(`${result.data.camera_name} 摄像头绑定成功！`);
                
                setTimeout(() => {
                    window.location.href = `${API_BASE}/monitor`;
                }, 1500);
            } else {
                showError(result.error || '绑定失败，请重试');
            }
        } catch (error) {
            console.error('Error:', error);
            showError('网络错误，请检查连接后重试');
        } finally {
            bindButton.disabled = false;
            loading.style.display = 'none';
        }
    });
    
    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.classList.remove('hidden');
        successMessage.classList.add('hidden');
    }
    
    function showSuccess(message) {
        successMessage.textContent = message;
        successMessage.classList.remove('hidden');
        errorMessage.classList.add('hidden');
    }
    
    function hideMessages() {
        errorMessage.classList.add('hidden');
        successMessage.classList.add('hidden');
    }
}

function initMonitorPage() {
    sessionId = localStorage.getItem('camera_session_id');
    const cameraName = localStorage.getItem('camera_name');
    
    const cameraImage = document.getElementById('cameraImage');
    const loadingOverlay = document.getElementById('loadingOverlay');
    const errorOverlay = document.getElementById('errorOverlay');
    const errorMessage = document.getElementById('errorMessage');
    const retryButton = document.getElementById('retryButton');
    const cameraNameDisplay = document.getElementById('cameraNameDisplay');
    const statusDot = document.getElementById('statusDot');
    const statusText = document.getElementById('statusText');
    
    if (!sessionId) {
        showError('会话已过期，请重新绑定摄像头');
        return;
    }
    
    if (cameraName) {
        cameraNameDisplay.textContent = cameraName;
    }
    
    retryButton.addEventListener('click', function() {
        errorOverlay.classList.add('hidden');
        startMonitoring();
    });
    
    function showError(message) {
        errorMessage.textContent = message;
        errorOverlay.classList.remove('hidden');
        loadingOverlay.classList.add('hidden');
        statusDot.classList.add('error');
        statusText.textContent = '连接失败';
    }
    
    function updateStatus(status) {
        statusDot.classList.remove('error', 'loading');
        
        if (status === 'loading') {
            statusDot.classList.add('loading');
            statusText.textContent = '连接中...';
        } else if (status === 'error') {
            statusDot.classList.add('error');
            statusText.textContent = '连接失败';
        } else {
            statusText.textContent = '已连接';
        }
    }
    
    async function fetchCameraInfo() {
        try {
            const response = await fetch(`${API_BASE}/info/${sessionId}`);
            const result = await response.json();
            
            if (result.success && result.data) {
                if (result.data.camera_name) {
                    cameraNameDisplay.textContent = result.data.camera_name;
                }
            }
        } catch (error) {
            console.error('Error fetching camera info:', error);
        }
    }
    
    async function fetchSnapshot() {
        try {
            const response = await fetch(`${API_BASE}/snapshot/${sessionId}`);
            
            if (response.ok) {
                const blob = await response.blob();
                
                if (blob.size > 0) {
                    const imageUrl = URL.createObjectURL(blob);
                    cameraImage.src = imageUrl;
                    
                    loadingOverlay.classList.add('hidden');
                    errorOverlay.classList.add('hidden');
                    updateStatus('connected');
                    
                    URL.revokeObjectURL(imageUrl);
                } else {
                    throw new Error('Empty response');
                }
            } else {
                throw new Error('Failed to fetch snapshot');
            }
        } catch (error) {
            console.error('Error fetching snapshot:', error);
            showError('无法获取摄像头画面，请检查摄像头是否正常工作');
            stopMonitoring();
        }
    }
    
    function startMonitoring() {
        loadingOverlay.classList.remove('hidden');
        updateStatus('loading');
        
        fetchCameraInfo();
        fetchSnapshot();
        
        if (refreshInterval) {
            clearInterval(refreshInterval);
        }
        
        refreshInterval = setInterval(() => {
            fetchSnapshot();
        }, 500);
    }
    
    function stopMonitoring() {
        if (refreshInterval) {
            clearInterval(refreshInterval);
            refreshInterval = null;
        }
    }
    
    window.addEventListener('beforeunload', function() {
        stopMonitoring();
    });
    
    startMonitoring();
}
