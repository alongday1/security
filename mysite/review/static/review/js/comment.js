document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('file-input').addEventListener('change', function(event) {
        const files = event.target.files;
        const allowedTypes = ['image/png', 'image/jpeg'];
        const maxSize = 2 * 1024 * 1024; // 2MB
        const maxFiles = 4; // 最多4张图片

        console.log('length', files.length); // 检查文件数量

        // 检查选择的图片数量是否超过4张
        if (files.length > maxFiles) {
            alert('最多只能上传4张图片');
            event.target.value = ''; // 清空已选择的文件
            return;
        }

        // 遍历检查每个文件
        for (let i = 0; i < files.length; i++) {
            const file = files[i];

            // 检查文件类型
            if (!allowedTypes.includes(file.type)) {
                alert('请上传PNG或JPG格式的图片');
                event.target.value = ''; // 清空已选择的文件
                return;
            }

            // 检查文件大小
            if (file.size > maxSize) {
                alert('每张图片文件不能超过2MB');
                event.target.value = ''; // 清空已选择的文件
                return;
            }
        }

        // 如果所有文件都符合要求，可以继续上传
        console.log('图片上传成功:', files);
    });

    init_chart();
});


// 星级评分
window.onload = function() {
    const stars = document.querySelectorAll('.star');
    const ratingOutputs = document.querySelectorAll('.rating-output');
    const ratingInputs = document.querySelectorAll('.rating-input');

    stars.forEach(star => {
        star.addEventListener('click', () => {
            const rating = star.getAttribute('data-value');

            // 更新星星的选中状态
            stars.forEach(s => {
                if (s.getAttribute('data-value') == rating) {
                    s.classList.add('selected');
                } else {
                    s.classList.remove('selected');
                }
            });

            // 显示当前评分
            ratingOutputs.forEach(ratingOutput => {
                ratingOutput.textContent = rating;
            })
            ratingInputs.forEach(ratingInput => {
                ratingInput.value = rating;
            })
        });
    });

    if (current_rating != '') {
        // 初始化星星的选中状态
        stars.forEach(s => {
            if (s.getAttribute('data-value') == current_rating) {
                s.classList.add('selected');
            } else {
                s.classList.remove('selected');
            }
        });
        ratingOutputs.forEach(ratingOutput => {
            ratingOutput.textContent = current_rating;
        })
        ratingInputs.forEach(ratingInput => {
            ratingInput.value = current_rating;
        })
    }
};


function init_chart(){
    console.log('rating_list:', rating_list);

    // 1. 创建一个包含 0 到 5 分的数组，并初始化每个分数的计数为 0
    const ratingCounts = Array(6).fill(0);

    // 2. 统计每个分数的出现次数
    rating_list.forEach(value => {
        if (value >= 0 && value <= 5) {
            ratingCounts[value]++;
        }
    });

    console.log('ratingCounts:', ratingCounts);

    // 3. 计算每个分数的百分比
    const totalRatings = rating_list.length;
    const ratingPercentages = ratingCounts.map(count => (count / totalRatings) * 100);
    // 找到最大百分比
    const maxPercentage = Math.max(...ratingPercentages);
    // 将每个百分比按最大值为 1 进行归一化
    const normalizedPercentages = ratingPercentages.map(percentage => 100*percentage / maxPercentage);

    console.log('ratingPercentages:', ratingPercentages);

    // 4. 获取 chart 容器
    const chart = document.getElementById('chart');
    chart.innerHTML = ''; // 清空图表内容，确保重新生成

    // 5. 按 5 到 0 的顺序创建条形和对应的分值标签
    for (let i = 5; i >= 0; i--) {
        // 创建条形容器
        const barContainer = document.createElement('div');
        barContainer.className = 'bar-container';
        barContainer.style.display = 'flex';
        barContainer.style.flexDirection = 'column';
        barContainer.style.alignItems = 'center';
        barContainer.style.height = '100%'; // 设置容器高度为100%
        barContainer.style.marginRight = '5px';

        // 创建条形
        height = normalizedPercentages[i];
        if (height == 0)
            height = 2;
        const hide_bar = document.createElement('div');
        hide_bar.className = 'hide_bar';
        hide_bar.style.height = `${100-height}%`; // 设置高度为百分比
        console.log('hide_bar height:', hide_bar.style.height);
        barContainer.appendChild(hide_bar);

        const bar = document.createElement('div');
        bar.className = 'bar';
        bar.style.height = `${height}%`; // 设置高度为百分比
        barContainer.appendChild(bar);
        barContainer.title = `${i} 分: ${ratingPercentages[i].toFixed(2)}%`; // 鼠标悬停时显示百分比

        // 创建分值标签
        const label = document.createElement('div');
        label.className = 'label';
        label.innerText = i; // 设置分值
        barContainer.appendChild(label);

        // 将条形容器添加到 chart 容器中
        chart.appendChild(barContainer);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    edit_button = document.getElementById('button-edit');
    edit_desc = document.getElementById('edit-desc');
    revise_tag = document.getElementById('tag-edit');

    edit_button.addEventListener('click', function(e) {
        e.preventDefault();
        if (!edit_button.classList.contains("activated"))
        {
            edit_button.classList.add("activated");
            edit_button.innerHTML = `完成`;
            edit_desc.classList.remove("hidden");
            revise_tag.classList.remove("hidden");
        }
        else
        {
            edit_button.classList.remove("activated");
            edit_button.innerHTML = `<i class="bi bi-pencil-square"></i>编辑菜品信息`;
            edit_desc.classList.add("hidden");
            revise_tag.classList.add("hidden");

            // 更新菜品信息
            const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
            fetch("update_dish_info/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    'X-CSRFToken': csrfToken // 添加 CSRF 令牌
                },
                body: JSON.stringify({
                    tags: tags,
                    desc: desc,
                    dish_id: dish_id // 同时传递多个参数
                })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error("网络响应不正常");
                }
                return response.json(); // 假设后端返回 JSON 数据
            })
            .then(data => {
                console.log("服务器响应:", data);
                alert("菜品信息修改成功！");
            })
            .catch(error => {
                console.error("请求发生错误:", error);
                alert("编辑时出现错误，请重试！");
            });
        }
    });

    init_tagModal();
    init_descModal();

});


function update_tags()
{
    var current_div = document.getElementById('tags_show');
    current_div.innerHTML = '';
    var tagHTML = '';
    tagHTML += `
        <div class="mx-1" style="margin-bottom:5px;color:#2b2b2b">
            标签：
        </div>
    `;
    tags.forEach(tag => {
        if (tag.length > 2)
        {
            tagHTML += `
                <div class="mx-1" style="margin-bottom: 5px;">
                    <button class="tag_button_lg disabled"><span style="color:#666666">#</span>${tag}</button>
                </div>
            `;
        }
        else
        {
            tagHTML += `
                <div class="mx-1" style="margin-bottom: 5px;font-family:'Noto Sans SC',sans-serif;">
                    <button class="tag_button disabled"><span style="color:#666666">#</span>${tag}</button>
                </div>
            `;
        }
    });
    current_div.innerHTML = tagHTML;
}


function init_tagModal() {
    // 生成标签按钮
    const tagContainer = document.getElementById('tagContainer');
    all_tags.forEach(tag => {
        const tagDiv = document.createElement('div');
        const tagButton = document.createElement('button');
        tagDiv.classList.add('d-flex');
        tagDiv.classList.add('justify-content-center');
        tagButton.textContent = tag;
        if (tag.length > 2)
        {
            tagDiv.classList.add('col-sm-4');
            tagButton.classList.add('tag-button-lg');
        }
        else
        {
            tagDiv.classList.add('col-sm-2');
            tagButton.classList.add('tag-button');
        }

        if (tags.includes(tag)) {
            tagButton.classList.add('selected');
        }

        tagButton.addEventListener('click', () => {
            tagButton.classList.toggle('selected'); // 点击切换选中状态
        });

        tagDiv.appendChild(tagButton);
        tagContainer.appendChild(tagDiv);
    });

    // 确认选择按钮
    const confirmButton = document.getElementById('confirmSelection');
    confirmButton.addEventListener('click', () => {
        // 获取所有已选中的标签
        const selectedTags = Array.from(document.querySelectorAll('.tag-button.selected, .tag-button-lg.selected'))
                                 .map(button => button.textContent);

        console.log('选中的标签:', selectedTags);
        tags = selectedTags;
        update_tags();

        // 关闭模态框
        tagModal = bootstrap.Modal.getInstance(document.getElementById("tagModal"));
            if (tagModal) {
                tagModal.hide();
                //document.querySelector('.modal-backdrop').remove();
            }
    });
}


function init_descModal() {
    document.getElementById("descInput").value = desc;

    // 确认按钮
    const confirmButton = document.getElementById('submitDesc');
    confirmButton.addEventListener('click', () => {
        current_desc = document.getElementById("descInput").value;
        console.log('描述：', current_desc);
        desc = current_desc;
        document.getElementById('desc-content').innerHTML = `${desc}`;

        // 关闭模态框
        descModal = bootstrap.Modal.getInstance(document.getElementById("descModal"));
            if (descModal) {
                descModal.hide();
            }
    });
}


document.addEventListener("DOMContentLoaded", function() {
    // 提交表单时处理数据
    document.getElementById("imageForm").onsubmit = function(event) {
        event.preventDefault();  // 阻止默认表单提交行为
        // 获取表单数据
        const formData = new FormData(this);

        // AJAX 请求将表单数据发送到后端
        fetch("add_image/", {
            method: "POST",
            body: formData,
            headers: {
                "X-CSRFToken": formData.get("csrfmiddlewaretoken"),  // Django 的 CSRF 保护
            },
        })
        .then(response => {
            if (!response.ok) {
                throw new Error("网络响应不正常");
            }
            return response.json();
        })
        .then(data => {
            // 处理服务器响应
            console.log("服务器响应:", data);
            alert("图片添加成功！");
            Modal = bootstrap.Modal.getInstance(document.getElementById("modal-addimage"));
            if (Modal) {
                Modal.hide();
                old_length = images.length;
                images = data.updated_images;
                console.log("updated images", images);
                container = document.getElementById("image-container");
                container.innerHTML = images.map((image_url, index) => `
                    ${(index % 4 === 0) ? `<div class="carousel-item ${(index === 0) ? 'active' : ''}"><div class="row text-center">` : ''}
                        <div class="col-md-3">
                            <img src="${image_url}" alt="Image ${index + 1}" class="d-block w-100" style="height: 250px; width: 300px; object-fit: cover;">
                        </div>
                    ${(index % 4 === 3 || index === images.length - 1) ? `</div></div>` : ''}
                `).join('');
                if (old_length == 0)
                {
                    document.getElementById('link-noimage').classList.add('hidden');
                    document.getElementById('link-addimage').classList.remove('hidden');
                }
            }
        })
        .catch(error => {
            console.error("请求发生错误:", error);
            alert("添加图片时出现错误，请重试！");
        });
    };
});


document.addEventListener("DOMContentLoaded", function() {
    show_mine = document.getElementById('show-mine');
    show_mine.addEventListener('click', function(e) {
        e.preventDefault();
        show_mine.classList.toggle("selected");
        search_comments();
    });

    submit_search = document.getElementById('submit-search');
    submit_search.addEventListener('click', function(e) {
        e.preventDefault();
        search_comments();
    });

});


function search_comments() {
    const searchText = document.getElementById('search-comment').value;
    const show_mine = document.getElementById('show-mine').classList.contains('selected');
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    fetch("refresh_comments/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            'X-CSRFToken': csrfToken // 添加 CSRF 令牌
        },
        body: JSON.stringify({
            dish_id: dish_id,
            search_text: searchText,
            show_mine: show_mine,
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("网络响应不正常");
        }
        return response.json(); // 假设后端返回 JSON 数据
    })
    .then(data => {
        const commentsContainer = document.getElementById('comments-page');
        commentsContainer.innerHTML = data.html; // 插入 HTML
        console.log("show_mine_success", data.show_mine_success);
        if (data.show_mine_success == 'false')
            alert("请先登录！");
    })
    .catch(error => {
        console.error("请求发生错误:", error);
        alert("搜索出现错误，请重试！");
    });
}
