document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('uploadForm');
    const uploadButton = document.getElementById('uploadButton');
    const loadingOverlay = document.getElementById('loadingOverlay');
    const resultContainer = document.getElementById('resultContainer');
    const fileNameElement = document.getElementById('fileName');
    const fileTypeElement = document.getElementById('fileType');
    const fileSizeElement = document.getElementById('fileSize');
    const resultContentElement = document.getElementById('resultContent');
    
    // 表单提交处理
    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(uploadForm);
        const fileInput = document.getElementById('file');
        const file = fileInput.files[0];
        
        if (!file) {
            alert('请选择一个文件');
            return;
        }
        
        // 显示加载状态
        loadingOverlay.classList.remove('hidden');
        
        // 上传文件
        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('上传失败');
            }
            return response.json();
        })
        .then(data => {
            // 隐藏加载状态
            loadingOverlay.classList.add('hidden');
            
            if (data.success) {
                // 显示结果
                resultContainer.classList.remove('hidden');
                
                // 填充文件信息
                fileNameElement.textContent = data.file_name;
                fileTypeElement.textContent = data.file_type;
                fileSizeElement.textContent = data.file_size;
                
                // 填充检测结果
                if (data.is_image) {
                    // 图片结果
                    resultContentElement.innerHTML = `
                        <div class="image-result">
                            <img src="data:image/jpeg;base64,${data.image_data}" alt="上传的图片" class="result-image">
                            <p><span class="label">是否检测到烟火:</span> <span class="result-value ${data.fire_detected ? 'fire-detected' : 'no-fire'}">${data.fire_detected ? '是' : '否'}</span></p>
                            ${data.fire_detected ? `<p><span class="label">置信度:</span> <span class="result-value">${(data.confidence * 100).toFixed(2)}%</span></p>` : ''}
                        </div>
                    `;
                } else {
                    // 视频结果
                    resultContentElement.innerHTML = `
                        <div class="video-result">
                            <p><span class="label">视频时长:</span> <span class="result-value">${data.video_duration} 秒</span></p>
                            <p><span class="label">检测到烟火的时间点:</span></p>
                            <ul class="timepoints-list">
                                ${data.fire_timepoints.map(time => `<li>${time} 秒</li>`).join('')}
                            </ul>
                        </div>
                    `;
                }
            } else {
                alert('处理失败: ' + data.error);
            }
        })
        .catch(error => {
            loadingOverlay.classList.add('hidden');
            alert('上传失败: ' + error.message);
        });
    });
});