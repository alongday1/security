// 切换选中状态
function toggleSelect(link) {
    const restaurantLinks = document.querySelectorAll('.restaurant-link');
    restaurantLinks.forEach(l => l.classList.remove('selected')); // 移除所有链接的选中状态
    link.classList.add('selected'); // 设置当前点击的链接为选中状态
    console.log(link.classList);
}


document.addEventListener('DOMContentLoaded', function() { // 确保在 DOM 文档加载完成后执行内部代码
    // 为所有具有 restaurant-link 类的元素绑定点击事件
    var restaurantLinks = document.querySelectorAll('.restaurant-link');
    restaurantLinks.forEach(function(link) {
        link.addEventListener('click', function(e) { // 为每个链接添加点击事件
            e.preventDefault(); // 阻止默认的点击事件，防止页面跳转或刷新
            toggleSelect(link);
            submitSearch();
        });
    });

    // 为id为search_submit的元素绑定点击事件
    var searchSubmitButton = document.getElementById('submit-search');
    if (searchSubmitButton) {
        searchSubmitButton.addEventListener('click', function(e) {
            e.preventDefault(); // 阻止默认的点击事件，防止页面跳转或刷新
            submitSearch();
        });
    }

    // 下拉菜单改变时刷新菜品列表
    document.getElementById('sort-category').addEventListener('change', submitSearch);
    document.getElementById('sort-order').addEventListener('change', submitSearch);

    submitSearch();
});


function submitSearch()
{
    // 当切换食堂、点击“搜索”按钮的时候被调用，作为提交搜索刷新菜品的函数
    // 首先获取被选中的食堂的id
    const restaurantLinks = document.querySelectorAll('.restaurant-link');
    var canteenId = null;
    // 找到选中的食堂
    restaurantLinks.forEach(link => {
        if (link.classList.contains('selected')) {
            canteenId = link.dataset.id; // 获取选中的链接的 ID
        }
    });
    console.log('submitSearch', canteenId);
    // 如果找到了选中的链接
    if (canteenId) {
        console.log('选中链接的 ID:', canteenId);
    } else {
        console.log('没有选中的链接');
        canteenId = '0'; // 当没选中时，设置食堂id为0，表示全部
    }

    // 然后获取tag，包括的tags和被排除的tags都直接在includedTags和excludedTags里面了
    // 最后获取名称
    var dishName = document.getElementById('dish_name').value;
    console.log('dishName', dishName);

    // 获取排序类型
    const category = document.getElementById('sort-category').value;
    const order = document.getElementById('sort-order').value;
    console.log("sort", category, order);

    // 清空之前的菜品内容
    document.getElementById('dish-list').innerHTML = '<p>加载中...</p>';

    // 构建请求参数
    const params = new URLSearchParams({
        canteen_id: canteenId,
        included_tags: Array.from(includedTags).join(','),
        excluded_tags: Array.from(excludedTags).join(','),
        search_name: dishName,
        sort_category: category,
        sort_order: order,
    });

    // 发起 fetch 请求
    fetch(`${getDishesUrl}?${params.toString()}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('网络响应不成功');
            }
            return response.json(); // 转换为JSON
        })
        .then(data => {
            var dishHtml = '';

            if (data.dishes.length == 0)
                dishHtml += `
                    <div style="font-size:26px;">暂无菜品<div>
                `;
            // 遍历菜品并生成 HTML
            data.dishes.forEach(dish => {
                let url = `comments?dish_id=${dish.id}`;
                let rating_str='';
                console.log('main_image', dish.image);
                if (dish.rating != null)
                    rating_str=`评分：${dish.rating.toFixed(1)}`;
                else rating_str="暂无评分";
                dishHtml += `
                    <div class="dish-container row"
                        data-url="${url}">
                        <div class="col-md-3" style="display: flex; align-items: center;">
                            <img src="${dish.image}" alt="${dish.name}">
                        </div>
                        <div class="col-md-6 main_show">
                            <div style="font-size: 25px; font-weight:bold;margin-bottom: 5px;">${dish.name}</div>
                            <div>
                                <span class="rating_show">${rating_str}</span>
                                <span class="count_show">${dish.count_comment}条评价</span>
                            </div>
                            <div>
                                <span>地点：${dish.canteen}</span>
                            </div>
                            <div>
                                描述：${dish.description}
                            </div>
                        </div>
                        <div class="col-md-3 row tags_show">
                            ${dish.tags.map((tag, index) => {
                                if (tag.length > 2)
                                    return `<div class="col-sm-6 d-flex justify-content-center" style="margin-bottom: 5px;">
                                                <button class="tag_button_lg">${tag}</button>
                                            </div>`;
                                else
                                    return `<div class="col-sm-3" style="margin-bottom: 5px;">
                                                <button class="tag_button_sm">${tag}</button>
                                            </div>`;
                            }).join('')}
                        </div>
                        <div style="clear: both;"></div>
                    </div>
                `;
            });

            document.getElementById("dish-list").innerHTML = dishHtml;

            // 为每个 dish-container 绑定点击事件，实现跳转
            document.querySelectorAll('.dish-container').forEach(container => {
                container.addEventListener('click', function() {
                    var url = this.getAttribute('data-url');
                    window.location.href = url;  // 跳转到菜品详情页面
                });
            });
        })
        .catch(error => {
            document.getElementById('dish-list').innerHTML = '<p>无法加载菜品，请稍后重试。</p>';
            console.error('Error fetching dishes:', error);
        });
}



function toggleInclude(tag)
{
    id = tag.dataset.id;
    if (tag.classList.contains('included'))
    {
        tag.classList.remove('included');
        tag.classList.add('excluded');
        includedTags.delete(id);
        excludedTags.add(id);
    }
    else if (tag.classList.contains('excluded'))
    {
        tag.classList.remove('excluded');
        excludedTags.delete(id);
    }
    else
    {
        tag.classList.add('included');
        includedTags.add(id);
    }
    console.log(includedTags);
    console.log(excludedTags);
}


document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("tagForm").onsubmit = function(event) {
        event.preventDefault();
        const formData = new FormData(this);

        fetch("add_tag/", {
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
            alert("标签已成功添加！");
        })
        .catch(error => {
            console.error("请求发生错误:", error);
            alert("添加失败，该标签已存在！");
        });
    };
});


// 动态加载食堂名称到下拉框
function loadCanteens() {
    console.log(canteen_list);
    const select = document.getElementById("canteenSelect");
    canteen_list.forEach(name => {
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        select.appendChild(option);
    });
}

// 加载食堂名称
document.addEventListener("DOMContentLoaded", loadCanteens);

document.addEventListener("DOMContentLoaded", function() {
    // 提交表单时处理数据
    document.getElementById("dishForm").onsubmit = function(event) {
        event.preventDefault();  // 阻止默认表单提交行为
        // 获取表单数据
        const formData = new FormData(this);

        // AJAX 请求将表单数据发送到后端
        fetch("add_dish/", {
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
            return response.json(); // 假设后端返回 JSON 数据
        })
        .then(data => {
            // 处理服务器响应
            console.log("服务器响应:", data);
            alert("菜品已成功添加！");
//            const dishModal = bootstrap.Modal.getInstance(document.getElementById("dishModal"));
//            if (dishModal) {
//                dishModal.hide();
//                document.querySelector('.modal-backdrop').remove();
//            }
        })
        .catch(error => {
            console.error("请求发生错误:", error);
            alert("添加菜品时出现错误，请重试！");
        });
    };
});




