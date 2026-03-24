document.addEventListener('DOMContentLoaded', function() {
    const cameraTypeSelect = document.getElementById('cameraType');
    const usbFields = document.getElementById('usbFields');
    const rtspFields = document.getElementById('rtspFields');
    const bindForm = document.getElementById('bindForm');
    const bindButton = document.getElementById('bindButton');
    const successMessage = document.getElementById('successMessage');
    const brandSelect = document.getElementById('brand');
    const modelSelect = document.getElementById('model');
    
    const cameraModels = {
        hikvision: ['DS-2CD2xxx', 'DS-2CD3xxx', 'DS-2CD4xxx', 'DS-2CD5xxx'],
        dahua: ['IPC-HFWxxx', 'IPC-HDBWxxx', 'IPC-HDWxxx', 'IPC-HFW5xxx'],
        axis: ['P1447-LE', 'P3225-LVE', 'Q1615', 'M3045-V'],
        bosch: ['NBN-xxx', 'NWC-xxx', 'FLEXIDOME', 'MICRODOME'],
        samsung: ['SNB-xxx', 'SNO-xxx', 'SNV-xxx', 'SND-xxx']
    };
    
    cameraTypeSelect.addEventListener('change', function() {
        const selectedType = this.value;
        
        usbFields.classList.add('hidden');
        rtspFields.classList.add('hidden');
        
        if (selectedType === 'usb') {
            usbFields.classList.remove('hidden');
            const usbInputs = usbFields.querySelectorAll('input, select');
            usbInputs.forEach(input => input.classList.add('error'));
        } else if (selectedType === 'rtsp') {
            rtspFields.classList.remove('hidden');
            const rtspInputs = rtspFields.querySelectorAll('input, select');
            rtspInputs.forEach(input => input.classList.add('error'));
        }
        
        validateField(this);
        validateForm();
    });
    
    brandSelect.addEventListener('change', function() {
        const selectedBrand = this.value;
        modelSelect.innerHTML = '<option value="">请选择型号</option>';
        modelSelect.classList.add('error');
        
        if (selectedBrand && cameraModels[selectedBrand]) {
            cameraModels[selectedBrand].forEach(model => {
                const option = document.createElement('option');
                option.value = model;
                option.textContent = model;
                modelSelect.appendChild(option);
            });
        }
        
        validateField(this);
        validateForm();
    });
    
    modelSelect.addEventListener('change', function() {
        validateField(this);
        validateForm();
    });
    
    const formInputs = bindForm.querySelectorAll('input, select');
    formInputs.forEach(input => {
        input.addEventListener('input', function() {
            validateField(this);
            validateForm();
        });
        input.addEventListener('blur', function() {
            validateField(this);
        });
    });
    
    function initializeInputStyles() {
        const allInputs = bindForm.querySelectorAll('input, select');
        allInputs.forEach(input => {
            input.classList.add('error');
        });
    }
    
    initializeInputStyles();
    
    function validateField(field) {
        const fieldName = field.name;
        const value = field.value.trim();
        
        field.classList.remove('error', 'success');
        
        if (field.hasAttribute('required') && !value) {
            field.classList.add('error');
            return false;
        }
        
        if (fieldName === 'cameraName' && value.length > 50) {
            field.classList.add('error');
            return false;
        }
        
        if (fieldName === 'ipAddress' && value) {
            const ipRegex = /^(\d{1,3}\.){3}\d{1,3}$/;
            if (!ipRegex.test(value)) {
                field.classList.add('error');
                return false;
            }
        }
        
        if (fieldName === 'port' && value) {
            const port = parseInt(value);
            if (port < 1 || port > 65535) {
                field.classList.add('error');
                return false;
            }
        }
        
        field.classList.add('success');
        return true;
    }
    
    function validateForm() {
        let isValid = true;
        
        const cameraType = cameraTypeSelect.value;
        if (!cameraType) {
            isValid = false;
        }
        
        const cameraName = document.getElementById('cameraName');
        if (!cameraName.value.trim() || cameraName.value.trim().length > 50) {
            isValid = false;
        }
        
        if (cameraType === 'rtsp') {
            const ipAddress = document.getElementById('ipAddress');
            const port = document.getElementById('port');
            const username = document.getElementById('username');
            const password = document.getElementById('password');
            
            if (!ipAddress.value.trim() || !validateIP(ipAddress.value.trim())) {
                isValid = false;
            }
            
            if (!port.value || parseInt(port.value) < 1 || parseInt(port.value) > 65535) {
                isValid = false;
            }
            
            if (!username.value.trim() || !password.value.trim()) {
                isValid = false;
            }
        }
        
        bindButton.disabled = !isValid;
        return isValid;
    }
    
    function validateIP(ip) {
        const ipRegex = /^(\d{1,3}\.){3}\d{1,3}$/;
        if (!ipRegex.test(ip)) return false;
        
        const parts = ip.split('.');
        for (let part of parts) {
            const num = parseInt(part);
            if (num < 0 || num > 255) return false;
        }
        return true;
    }
    
    bindForm.addEventListener('submit', async function(e) {
        console.log('表单提交事件触发');
        e.preventDefault();
        
        if (!validateForm()) {
            console.log('表单验证失败');
            return;
        }
        
        console.log('开始绑定摄像头...');
        const formData = new FormData(bindForm);
        const data = {
            cameraType: formData.get('cameraType'),
            name: formData.get('cameraName')
        };
        console.log('提交的数据:', data);
        
        if (data.cameraType === 'usb') {
            data.deviceIndex = parseInt(formData.get('deviceIndex'));
        } else if (data.cameraType === 'rtsp') {
            data.ip = formData.get('ipAddress');
            data.port = parseInt(formData.get('port'));
            data.username = formData.get('username');
            data.password = formData.get('password');
            data.brand = formData.get('brand');
            data.model = formData.get('model');
        }
        
        bindButton.disabled = true;
        bindButton.textContent = '绑定中...';
        
        try {
            const response = await fetch('/api/camera/bind', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.success) {
                const sessionData = {
                    sessionId: result.sessionId,
                    cameraName: data.name,
                    timestamp: Date.now()
                };
                localStorage.setItem('cameraSession', JSON.stringify(sessionData));
                
                successMessage.textContent = `${data.name}摄像头绑定成功！`;
                successMessage.classList.remove('hidden');
                
                setTimeout(() => {
                    window.location.href = '/monitor';
                }, 3000);
            } else {
                alert(result.error || '绑定失败，请重试');
                bindButton.disabled = false;
                bindButton.textContent = '绑定摄像头';
            }
        } catch (error) {
            alert('网络错误，请检查连接');
            bindButton.disabled = false;
            bindButton.textContent = '绑定摄像头';
        }
    });
    
    const sessionData = localStorage.getItem('cameraSession');
    const urlParams = new URLSearchParams(window.location.search);
    const fromExit = urlParams.get('exit');
    
    if (sessionData && !fromExit) {
        try {
            const session = JSON.parse(sessionData);
            const now = Date.now();
            const hoursSinceLastActivity = (now - session.timestamp) / (1000 * 60 * 60);
            
            if (hoursSinceLastActivity < 24) {
                window.location.href = '/monitor';
            } else {
                localStorage.removeItem('cameraSession');
            }
        } catch (e) {
            localStorage.removeItem('cameraSession');
        }
    }
});
