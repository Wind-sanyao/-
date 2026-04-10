document.addEventListener('DOMContentLoaded', function() {
    const sessionId = window.location.pathname.split('/').pop();
    const loadingOverlay = document.getElementById('loadingOverlay');
    const errorOverlay = document.getElementById('errorOverlay');
    const errorMessage = document.getElementById('errorMessage');
    const retryButton = document.getElementById('retryButton');
    const exitButton = document.getElementById('exitButton');
    const detectionFrame = document.getElementById('detectionFrame');
    const fireStatus = document.getElementById('fireStatus');
    const confidence = document.getElementById('confidence');
    const lastDetectionTime = document.getElementById('lastDetectionTime');
    const detectionStatus = document.getElementById('detectionStatus');
    
    let isConnected = false;
    let reconnectAttempts = 0;
    const maxReconnectAttempts = 5;
    
    // 连接摄像头
    function connectCamera() {
        loadingOverlay.classList.remove('hidden');
        errorOverlay.classList.add('hidden');
        
        fetch(`/api/camera/info/${sessionId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('连接失败');
                }
                return response.json();
            })
            .then(data => {
                // 无论状态如何，都设置为已连接并开始流式传输
                isConnected = true;
                loadingOverlay.classList.add('hidden');
                startStreaming();
            })
            .catch(error => {
                // 即使出错，也设置为已连接并开始流式传输
                isConnected = true;
                loadingOverlay.classList.add('hidden');
                startStreaming();
            });
    }
    
    // 开始流式传输
    function startStreaming() {
        // 更新检测画面
        function updateDetectionFrame() {
            if (!isConnected) return;
            
            console.log('尝试获取检测画面...');
            
            fetch(`/api/camera/detection/${sessionId}`)
                .then(response => {
                    console.log('获取检测画面响应状态:', response.status);
                    if (!response.ok) {
                        return response.json().then(data => {
                            throw new Error(data.error || '获取检测画面失败');
                        });
                    }
                    return response.blob();
                })
                .then(blob => {
                    console.log('获取检测画面成功，大小:', blob.size);
                    const url = URL.createObjectURL(blob);
                    detectionFrame.src = url;
                    setTimeout(updateDetectionFrame, 500);
                })
                .catch(error => {
                    console.error('更新检测画面失败:', error);
                    // 继续尝试获取画面
                    setTimeout(updateDetectionFrame, 1000);
                });
        }
        
        // 更新检测状态
        function updateDetectionStatus() {
            if (!isConnected) return;
            
            fetch(`/api/camera/detection/status/${sessionId}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('获取检测状态失败');
                    }
                    return response.json();
                })
                .then(data => {
                    fireStatus.textContent = data.fire_detected ? '检测到火灾' : '正常';
                    fireStatus.style.color = data.fire_detected ? '#c62828' : '#2e7d32';
                    
                    confidence.textContent = data.confidence ? `${(data.confidence * 100).toFixed(2)}%` : '--';
                    
                    if (data.last_detection_time) {
                        const date = new Date(data.last_detection_time * 1000);
                        lastDetectionTime.textContent = date.toLocaleString();
                    } else {
                        lastDetectionTime.textContent = '--';
                    }
                    
                    detectionStatus.textContent = '检测中';
                    detectionStatus.style.background = '#e0e0e0';
                    detectionStatus.style.color = '#666';
                    
                    setTimeout(updateDetectionStatus, 1000);
                })
                .catch(error => {
                    console.error('更新检测状态失败:', error);
                    detectionStatus.textContent = '检测失败';
                    detectionStatus.style.background = '#ffebee';
                    detectionStatus.style.color = '#c62828';
                    setTimeout(updateDetectionStatus, 2000);
                });
        }
        
        updateDetectionFrame();
        updateDetectionStatus();
    }
    
    // 显示错误
    function showError(message) {
        errorMessage.textContent = message;
        loadingOverlay.classList.add('hidden');
        errorOverlay.classList.remove('hidden');
        
        reconnectAttempts++;
        if (reconnectAttempts < maxReconnectAttempts) {
            setTimeout(connectCamera, 3000);
        }
    }
    
    // 重试连接
    retryButton.addEventListener('click', function() {
        reconnectAttempts = 0;
        connectCamera();
    });
    
    // 退出监控
    exitButton.addEventListener('click', function() {
        fetch(`/api/camera/unbind/${sessionId}`, {
            method: 'DELETE'
        })
        .then(() => {
            window.location.href = '/';
        })
        .catch(error => {
            console.error('退出监控失败:', error);
            window.location.href = '/';
        });
    });
    
    // 初始化
    connectCamera();
    
    // 页面关闭时清理
    window.addEventListener('beforeunload', function() {
        fetch(`/api/camera/unbind/${sessionId}`, {
            method: 'DELETE'
        });
    });
});
