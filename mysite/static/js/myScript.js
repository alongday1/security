function translation() {
    document.getElementById("教育背景title").innerHTML ="Educational Background: ";
    document.getElementById("教育背景").innerHTML ="Junior majoring in Information Security, School of Electronic Information and Electrical Engineering, Shanghai Jiao Tong University";
    document.getElementById("课业经历标题").innerHTML ="Academic Experience: ";
    document.getElementById("课业经历").innerHTML =
   "I have consistently approached each course with diligence, achieving a core course GPA of 4.05 out of 4.3. In these 2 year, I attained the highest grade point average and course credit accumulation within the major. I’ve excelled with scores of 95 and above in most foundational mathematics and computer-related courses, while maintaining an overall academic performance of 90 and above in other major courses.";

    document.getElementById(id="CtoE").style.backgroundColor = "#1f3149";
    document.getElementById(id="CtoE").style.color = "white";
    document.getElementById(id="CtoE").style.cursor = "not-allowed";

    document.getElementById(id="EtoC").style.backgroundColor = "LightSteelBlue";
    document.getElementById(id="EtoC").style.color = "black";
    document.getElementById(id="EtoC").style.cursor = "pointer";
}

function retranslation(){
    document.getElementById("教育背景title").innerHTML ="教育背景：";
    document.getElementById("教育背景").innerHTML ="上海交通大学 电子信息与电气工程学院 信息安全专业 大三年级在读";
    document.getElementById("课业经历标题").innerHTML ="课业经历：";
    document.getElementById("课业经历").innerHTML =
   "我始终认真对待各门课程，核心课程绩点4.05/4.3，学积分、绩点排名年级第一。数学基础类课程和计算机相关课程中基本取得95+，其余专业课总体保持在90+。";

    document.getElementById(id="EtoC").style.backgroundColor = "#1f3149";
    document.getElementById(id="EtoC").style.color = "white";
    document.getElementById(id="EtoC").style.cursor = "not-allowed";

    document.getElementById(id="CtoE").style.backgroundColor = "LightSteelBlue";
    document.getElementById(id="CtoE").style.color = "black";
    document.getElementById(id="CtoE").style.cursor = "pointer";
}