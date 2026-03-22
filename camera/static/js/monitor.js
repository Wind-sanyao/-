document.addEventListener('DOMContentLoaded', function() {
    const videoFrame = document.getElementById('videoFrame');
    const loadingOverlay = document.getElementById('loadingOverlay');
    const errorOverlay = document.getElementById('errorOverlay');
    const errorMessage = document.getElementById('errorMessage');
    const retryButton = document.getElementById('retryButton');
    const cameraNameElement = document.getElementById('cameraName');
    
    let sessionId = null;
    let cameraName = '';
    let refreshInterval = null;
    let isConnecting = false;
    
    function getSessionData() {
        const sessionData = localStorage.getItem('cameraSession');
        if (!sessionData) {
            return null;
        }
        
        try {
            const session = JSON.parse(sessionData);
            const now = Date.now();
            const hoursSinceLastActivity = (now - session.timestamp) / (1000 * 60 * 60);
            
            if (hoursSinceLastActivity >= 24) {
                localStorage.removeItem('cameraSession');
                return null;
            }
            
            return session;
        } catch (e) {
            localStorage.removeItem('cameraSession');
            return null;
        }
    }
    
    function updateSessionTimestamp() {
        const sessionData = localStorage.getItem('cameraSession');
        if (sessionData) {
            try {
                const session = JSON.parse(sessionData);
                session.timestamp = Date.now();
                localStorage.setItem('cameraSession', JSON.stringify(session));
            } catch (e) {
                localStorage.removeItem('cameraSession');
            }
        }
    }
    
    async function fetchCameraInfo() {
        try {
            const response = await fetch(`/api/camera/info/${sessionId}`);
            
            if (response.status === 404) {
                showError('会话不存在，请重新绑定');
                return null;
            }
            
            const data = await response.json();
            
            if (data.error) {
                showError(data.error);
                return null;
            }
            
            if (data.status === 'error') {
                showError(data.error || '摄像头连接错误');
                return null;
            }
            
            return data;
        } catch (error) {
            showError('网络错误，请检查连接');
            return null;
        }
    }
    
    function loadSnapshot() {
        if (!sessionId) {
            return;
        }
        
        const timestamp = Date.now();
        videoFrame.src = `/api/camera/snapshot/${sessionId}?t=${timestamp}`;
        
        updateSessionTimestamp();
    }
    
    function showLoading() {
        loadingOverlay.classList.remove('hidden');
        errorOverlay.classList.add('hidden');
    }
    
    function hideLoading() {
        loadingOverlay.classList.add('hidden');
    }
    
    function showError(message) {
        hideLoading();
        errorMessage.textContent = message;
        errorOverlay.classList.remove('hidden');
        stopMonitoring();
    }
    
    function startMonitoring() {
        if (refreshInterval) {
            clearInterval(refreshInterval);
        }
        
        loadSnapshot();
        refreshInterval = setInterval(loadSnapshot, 500);
    }
    
    function stopMonitoring() {
        if (refreshInterval) {
            clearInterval(refreshInterval);
            refreshInterval = null;
        }
    }
    
    async function connectCamera() {
        if (isConnecting) {
            return;
        }
        
        isConnecting = true;
        showLoading();
        
        const sessionData = getSessionData();
        
        if (!sessionData) {
            showError('会话已过期，请重新绑定');
            isConnecting = false;
            return;
        }
        
        sessionId = sessionData.sessionId;
        cameraName = sessionData.cameraName;
        cameraNameElement.textContent = cameraName;
        
        const cameraInfo = await fetchCameraInfo();
        
        if (cameraInfo) {
            hideLoading();
            startMonitoring();
        }
        
        isConnecting = false;
    }
    
    videoFrame.addEventListener('load', function() {
        hideLoading();
    });
    
    videoFrame.addEventListener('error', function() {
        if (!isConnecting) {
            showError('无法加载摄像头画面');
        }
    });
    
    retryButton.addEventListener('click', function() {
        localStorage.removeItem('cameraSession');
        window.location.href = '/';
    });
    
    document.addEventListener('visibilitychange', function() {
        if (document.hidden) {
            stopMonitoring();
        } else {
            connectCamera();
        }
    });
    
    window.addEventListener('beforeunload', function() {
        stopMonitoring();
    });
    
    connectCamera();
});
