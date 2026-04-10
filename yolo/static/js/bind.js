document.addEventListener('DOMContentLoaded', function() {
    const cameraType = document.getElementById('cameraType');
    const usbFields = document.getElementById('usbFields');
    const rtspFields = document.getElementById('rtspFields');
    const bindButton = document.getElementById('bindButton');
    const cameraInfo = document.getElementById('cameraInfo');
    const cameraName = document.getElementById('cameraName');
    const deviceIndex = document.getElementById('deviceIndex');
    const ipAddress = document.getElementById('ipAddress');
    const port = document.getElementById('port');
    const username = document.getElementById('username');
    const password = document.getElementById('password');
    const brand = document.getElementById('brand');
    
    // 监听摄像头类型变化
    cameraType.addEventListener('change', function() {
        if (this.value === 'usb') {
            usbFields.classList.remove('hidden');
            rtspFields.classList.add('hidden');
        } else if (this.value === 'rtsp') {
            rtspFields.classList.remove('hidden');
            usbFields.classList.add('hidden');
        } else {
            usbFields.classList.add('hidden');
            rtspFields.classList.add('hidden');
        }
        checkFormValidity();
    });
    
    // 监听摄像头信息选择
    cameraInfo.addEventListener('change', function() {
        if (this.value) {
            // 通过API获取摄像头详细信息并填充表单
            const cameraId = this.value;
            
            // 显示加载状态
            const originalText = bindButton.textContent;
            bindButton.disabled = true;
            bindButton.textContent = '加载中...';
            
            fetch('/api/cameras')
                .then(response => {
                    if (!response.ok) {
                        if (response.status === 401) {
                            // 会话过期，重定向到登录页面
                            window.location.href = '/login';
                            return Promise.reject('Session expired');
                        }
                        return response.json();
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.error) {
                        console.error('Error:', data.error);
                        // 恢复按钮状态
                        bindButton.disabled = false;
                        bindButton.textContent = originalText;
                        return;
                    }
                    
                    // 找到选中的摄像头
                    const selectedCamera = data.find(camera => camera.id == cameraId);
                    if (selectedCamera) {
                        // 填充表单
                        cameraType.value = selectedCamera.source_type;
                        cameraType.dispatchEvent(new Event('change'));
                        cameraName.value = selectedCamera.name;
                        
                        if (selectedCamera.source_type === 'usb') {
                            // 对于USB摄像头，使用source_url作为设备索引
                            deviceIndex.value = selectedCamera.source_url;
                        } else if (selectedCamera.source_type === 'rtsp') {
                            // 对于网络摄像头，尝试从source_url中提取信息
                            // 或者使用camera对象中的其他字段
                            if (selectedCamera.ip_address) {
                                ipAddress.value = selectedCamera.ip_address;
                            } else {
                                // 尝试从URL中提取IP
                                const urlMatch = selectedCamera.source_url.match(/rtsp:\/\/[^@]+@([^:]+):/);
                                if (urlMatch) {
                                    ipAddress.value = urlMatch[1];
                                }
                            }
                            
                            if (selectedCamera.port) {
                                port.value = selectedCamera.port;
                            } else {
                                // 尝试从URL中提取端口
                                const portMatch = selectedCamera.source_url.match(/:(\d+)\//);
                                if (portMatch) {
                                    port.value = portMatch[1];
                                } else {
                                    port.value = '554'; // 默认端口
                                }
                            }
                            
                            if (selectedCamera.username) {
                                username.value = selectedCamera.username;
                            } else {
                                // 尝试从URL中提取用户名
                                const userMatch = selectedCamera.source_url.match(/rtsp:\/\/([^:]+):/);
                                if (userMatch) {
                                    username.value = userMatch[1];
                                }
                            }
                            
                            if (selectedCamera.password) {
                                password.value = selectedCamera.password;
                            } else {
                                // 尝试从URL中提取密码
                                const passMatch = selectedCamera.source_url.match(/rtsp:\/\/[^:]+:([^@]+)@/);
                                if (passMatch) {
                                    password.value = passMatch[1];
                                }
                            }
                            
                            if (selectedCamera.brand) {
                                brand.value = selectedCamera.brand;
                            }
                        }
                        
                        // 填充后检查表单有效性
                        checkFormValidity();
                    }
                    
                    // 恢复按钮状态
                    bindButton.disabled = false;
                    bindButton.textContent = originalText;
                })
                .catch(error => {
                    console.error('Error:', error);
                    // 只有在不是会话过期的情况下才恢复按钮状态
                    if (error !== 'Session expired') {
                        // 恢复按钮状态
                        bindButton.disabled = false;
                        bindButton.textContent = originalText;
                    }
                });
        }
    });
    

    
    // 检查表单有效性
    function checkFormValidity() {
        // 检查当前显示的是哪个界面
        const existingCameraSection = document.getElementById('existingCameraSection');
        const newCameraSection = document.getElementById('newCameraSection');
        
        // 如果显示的是已有摄像头界面
        if (existingCameraSection.style.display !== 'none') {
            const cameraInfoValue = cameraInfo.value;
            if (cameraInfoValue) {
                bindButton.disabled = false;
                console.log('已有摄像头表单有效，启用绑定按钮');
            } else {
                bindButton.disabled = true;
                console.log('已有摄像头表单无效，禁用绑定按钮');
            }
        }
        // 如果显示的是新摄像头界面
        else if (newCameraSection.style.display !== 'none') {
            const cameraTypeValue = cameraType.value;
            const cameraNameValue = cameraName.value;
            
            console.log('检查新摄像头表单有效性:', {
                cameraTypeValue,
                cameraNameValue,
                ipAddress: ipAddress.value,
                port: port.value,
                username: username.value,
                password: password.value
            });
            
            if (cameraTypeValue && cameraNameValue) {
                if (cameraTypeValue === 'usb') {
                    bindButton.disabled = false;
                    console.log('USB摄像头表单有效，启用绑定按钮');
                } else if (cameraTypeValue === 'rtsp') {
                    const ipValue = ipAddress.value;
                    const portValue = port.value;
                    const usernameValue = username.value;
                    const passwordValue = password.value;
                    
                    if (ipValue && portValue && usernameValue && passwordValue) {
                        bindButton.disabled = false;
                        console.log('RTSP摄像头表单有效，启用绑定按钮');
                    } else {
                        bindButton.disabled = true;
                        console.log('RTSP摄像头表单无效，禁用绑定按钮');
                    }
                }
            } else {
                bindButton.disabled = true;
                console.log('新摄像头表单无效，禁用绑定按钮');
            }
        }
    }
    
    // 监听表单输入变化
    cameraInfo.addEventListener('change', checkFormValidity);
    cameraName.addEventListener('input', checkFormValidity);
    ipAddress.addEventListener('input', checkFormValidity);
    port.addEventListener('input', checkFormValidity);
    username.addEventListener('input', checkFormValidity);
    password.addEventListener('input', checkFormValidity);
    
    // 测试摄像头功能
    const testCameraButton = document.getElementById('testCameraButton');
    if (testCameraButton) {
        testCameraButton.addEventListener('click', function() {
            const deviceIndex = document.getElementById('deviceIndex').value;
            const testResult = document.getElementById('cameraTestResult');
            
            testResult.textContent = '测试中...';
            testResult.className = 'test-result testing';
            testCameraButton.disabled = true;
            
            fetch('/api/camera/test', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ deviceIndex: deviceIndex })
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(data => {
                        throw new Error(data.error || '测试失败');
                    });
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    testResult.textContent = '测试成功！摄像头可用';
                    testResult.className = 'test-result success';
                } else {
                    testResult.textContent = `测试失败: ${data.error}`;
                    testResult.className = 'test-result error';
                }
            })
            .catch(error => {
                testResult.textContent = `测试失败: ${error.message}`;
                testResult.className = 'test-result error';
            })
            .finally(() => {
                testCameraButton.disabled = false;
            });
        });
    }
    
    // 表单提交处理
    document.getElementById('bindForm').addEventListener('submit', function(e) {
        e.preventDefault(); // 阻止默认表单提交
        
        // 显示加载状态
        bindButton.disabled = true;
        bindButton.textContent = '绑定中...';
        
        console.log('表单提交，正在绑定摄像头...');
        
        // 检查当前显示的是哪个界面
        const existingCameraSection = document.getElementById('existingCameraSection');
        const newCameraSection = document.getElementById('newCameraSection');
        
        let formData = {};
        
        // 如果显示的是已有摄像头界面
        if (existingCameraSection.style.display !== 'none') {
            const cameraId = cameraInfo.value;
            formData = { cameraId: cameraId };
        }
        // 如果显示的是新摄像头界面
        else if (newCameraSection.style.display !== 'none') {
            const cameraTypeValue = cameraType.value;
            const cameraNameValue = cameraName.value;
            
            if (cameraTypeValue === 'usb') {
                const deviceIndexValue = deviceIndex.value;
                formData = {
                    cameraType: cameraTypeValue,
                    name: cameraNameValue,
                    deviceIndex: deviceIndexValue
                };
            } else if (cameraTypeValue === 'rtsp') {
                const ipValue = ipAddress.value;
                const portValue = port.value;
                const usernameValue = username.value;
                const passwordValue = password.value;
                const brandValue = brand.value;
                
                formData = {
                    cameraType: cameraTypeValue,
                    name: cameraNameValue,
                    ipAddress: ipValue,
                    port: portValue,
                    username: usernameValue,
                    password: passwordValue,
                    brand: brandValue
                };
            }
        }
        
        console.log('提交的表单数据:', formData);
        
        // 使用AJAX提交表单
        fetch('/api/camera/bind', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || '绑定失败');
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                console.log('绑定成功，会话ID:', data.sessionId);
                // 跳转到监控页面
                window.location.href = `/monitor/${data.sessionId}`;
            } else {
                throw new Error(data.error || '绑定失败');
            }
        })
        .catch(error => {
            console.error('绑定失败:', error);
            // 显示错误信息
            alert('绑定失败: ' + error.message);
            // 恢复按钮状态
            bindButton.disabled = false;
            bindButton.textContent = '绑定摄像头';
        });
    });
});
