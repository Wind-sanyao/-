document.addEventListener('DOMContentLoaded', function() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabPanes = document.querySelectorAll('.tab-pane');
    const tabButtonsContainer = document.querySelector('.tab-buttons');
    const loadingOverlay = document.getElementById('loadingOverlay');
    const resultContainer = document.getElementById('resultContainer');
    const fileNameElement = document.getElementById('fileName');
    const fileTypeElement = document.getElementById('fileType');
    const fileSizeElement = document.getElementById('fileSize');
    const resultContentElement = document.getElementById('resultContent');
    
    // 选项卡切换逻辑
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tab = this.getAttribute('data-tab');
            
            // 移除所有活动状态
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabPanes.forEach(pane => pane.classList.remove('active'));
            
            // 添加当前活动状态
            this.classList.add('active');
            document.getElementById(`${tab}-tab`).classList.add('active');
            
            // 更新背景滑动效果
            tabButtonsContainer.className = 'tab-buttons';
            tabButtonsContainer.classList.add(`${tab}-active`);
        });
    });
    
    // 表单提交处理函数
    function handleFormSubmit(form, url) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(form);
            const fileInput = form.querySelector('input[type="file"]');
            const files = fileInput.files;
            
            if (!files || files.length === 0) {
                alert('请选择文件');
                return;
            }
            
            // 显示加载状态
            loadingOverlay.classList.remove('hidden');
            
            // 上传文件
            fetch(url, {
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
                    fileNameElement.textContent = data.file_name || data.files_count + ' 个文件';
                    fileTypeElement.textContent = data.file_type || '文件夹';
                    fileSizeElement.textContent = data.file_size || '';
                    
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
                    } else if (data.is_gif) {
                        // GIF结果
                        resultContentElement.innerHTML = `
                            <div class="gif-result">
                                ${data.annotated_gif ? `
                                    <img src="data:image/gif;base64,${data.annotated_gif}" alt="检测结果GIF" class="result-image">
                                ` : ''}
                                <p><span class="label">GIF时长:</span> <span class="result-value">${data.gif_duration} 秒</span></p>
                                <p><span class="label">是否检测到烟火:</span> <span class="result-value ${data.fire_detected ? 'fire-detected' : 'no-fire'}">${data.fire_detected ? '是' : '否'}</span></p>
                                ${data.fire_timepoints && data.fire_timepoints.length > 0 ? `
                                    <p><span class="label">检测到烟火的时间点:</span></p>
                                    <ul class="timepoints-list">
                                        ${data.fire_timepoints.map(time => `<li>${time} 秒</li>`).join('')}
                                    </ul>
                                    <button class="export-button" onclick="exportCSV(${JSON.stringify(data.fire_timepoints)}, '${data.file_name}', 'gif')">导出检测结果</button>
                                ` : ''}
                            </div>
                        `;
                    } else if (data.is_folder) {
                        // 文件夹结果
                        resultContentElement.innerHTML = `
                            <div class="folder-result">
                                <p><span class="label">处理文件数:</span> <span class="result-value">${data.files_count}</span></p>
                                <p><span class="label">检测到烟火的文件数:</span> <span class="result-value ${data.fire_detected_count}">${data.fire_detected_count}</span></p>
                                ${data.fire_files ? `
                                    <p><span class="label">检测到烟火的文件:</span></p>
                                    <ul class="fire-files-list">
                                        ${data.fire_files.map(file => `<li>${file}</li>`).join('')}
                                    </ul>
                                    <button class="export-button" onclick="exportFolderCSV(${JSON.stringify(data.fire_files)}, '${data.file_name}')">导出检测结果</button>
                                ` : ''}
                            </div>
                        `;
                    } else if (data.is_video) {
                        // 视频结果
                        resultContentElement.innerHTML = `
                            <div class="video-result">
                                ${data.annotated_video ? `
                                    <img src="data:image/gif;base64,${data.annotated_video}" alt="检测结果视频" class="result-image">
                                ` : ''}
                                <p><span class="label">视频时长:</span> <span class="result-value">${data.video_duration} 秒</span></p>
                                <p><span class="label">是否检测到烟火:</span> <span class="result-value ${data.fire_detected ? 'fire-detected' : 'no-fire'}">${data.fire_detected ? '是' : '否'}</span></p>
                                ${data.fire_timepoints && data.fire_timepoints.length > 0 ? `
                                    <p><span class="label">检测到烟火的时间点:</span></p>
                                    <ul class="timepoints-list">
                                        ${data.fire_timepoints.map(time => `<li>${time} 秒</li>`).join('')}
                                    </ul>
                                    <button class="export-button" onclick="exportCSV(${JSON.stringify(data.fire_timepoints)}, '${data.file_name}', 'video')">导出检测结果</button>
                                ` : ''}
                            </div>
                        `;
                    } else {
                        // 其他结果
                        resultContentElement.innerHTML = `
                            <div class="other-result">
                                <p>处理完成</p>
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
    }
    
    // 绑定表单提交事件
    const imageForm = document.getElementById('imageForm');
    const videoForm = document.getElementById('videoForm');
    const folderForm = document.getElementById('folderForm');
    
    if (imageForm) handleFormSubmit(imageForm, '/upload');
    if (videoForm) handleFormSubmit(videoForm, '/upload');
    if (folderForm) handleFormSubmit(folderForm, '/upload/folder');

    // 导出CSV函数
    window.exportCSV = function(timepoints, fileName, fileType) {
        // 创建CSV内容
        let csvContent = '检测到烟火的时间点,置信度\n';
        
        // 时间点列表，置信度默认为90%
        timepoints.forEach(time => {
            csvContent += `${time},90\n`;
        });
        
        // 创建Blob对象
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        
        // 创建下载链接
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        
        // 设置文件名
        const timestamp = new Date().toISOString().slice(0, 19).replace(/[:T]/g, '-');
        const csvFileName = `${fileType}_detection_${fileName.replace(/\.[^/.]+$/, '')}_${timestamp}.csv`;
        
        // 触发下载
        link.setAttribute('href', url);
        link.setAttribute('download', csvFileName);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    // 导出文件夹CSV函数
    window.exportFolderCSV = function(fireFiles, folderName) {
        // 创建CSV内容
        let csvContent = '检测到烟火的文件\n';
        
        // 遍历文件列表
        fireFiles.forEach(file => {
            csvContent += `${file}\n`;
        });
        
        // 创建Blob对象
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        
        // 创建下载链接
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        
        // 设置文件名
        const timestamp = new Date().toISOString().slice(0, 19).replace(/[:T]/g, '-');
        const csvFileName = `folder_detection_${folderName.replace(/\.[^/.]+$/, '')}_${timestamp}.csv`;
        
        // 触发下载
        link.setAttribute('href', url);
        link.setAttribute('download', csvFileName);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };
});