/**
 * Created by xiangfeng on 2016/11/14.
 */
$(function(){
	$('#close_im').bind('click',function(){
		$('#main-im').css("height","0");
		$('#im_main').hide();
		$('#open_im').show();
	});
	$('#open_im').bind('click',function(e){
		$('#main-im').css("height","272");
		$('#im_main').show();
		$(this).hide();
	});
	$('.go-top').bind('click',function(){
		$(window).scrollTop(0);
	});
	$(".weixing-container").bind('mouseenter',function(){
		$('.weixing-show').show();
	})
	$(".weixing-container").bind('mouseleave',function(){
		$('.weixing-show').hide();
	});
});

function getformvalues(id) {
    var values = new Object();
    $('#' + id + ' input').each(function () {
        if ($(this).attr('name') && $(this).val() && $(this).attr('data-formnotget') == undefined)
            values[$(this).attr('name')] = $(this).val();
    });
    $('#' + id + ' select').each(function () {
        if ($(this).attr('name') && $(this).val())
            values[$(this).attr('name')] = $(this).val();
    });
    return values;
}


function newPerageInfo(obj){
    var per_page = $(obj).val();
    var urlpara = window.location.search.replace(/\?/,'').split('&');
    var para1 = '';
    var para2 = '';
    for(i in urlpara)
    {
        if(urlpara[i].indexOf('page=') != -1){}
        else{para2 += '&' + urlpara[i];}
    }
    var para1 = '?perpage=' + per_page;
    window.location = window.location.pathname + para1 + para2;
}


var defaulttime = 5;
function showTips( tips, time , type){
    var windowWidth = window.screen.width;
    var windowHeight = window.screen.height;

    if(time == undefined)
        time = defaulttime;

    if(type == undefined)
        type = 'alert';
    var color = 'green';
    if(type == 'alert')
        color = 'red';
    else if(type == 'success')
        color = 'green';
    $('#optip #optip-content').html(tips).css({'color': color});
    $('#optip').css({
        'top' : ( windowHeight / 2 ) - 100 + 'px',
        'left' : ( windowWidth / 2 ) - 100 + 'px',
        'height': '0'
    }).show();
    $('#optip').animate({height:"70px"}).focus();
    setTimeout( function(){$('#optip').fadeOut();}, ( time * 1000 ) );
}

function userAction(obj){
    var domain = $(obj).attr('content');
    var url = $(obj).attr('href');
    $.post('/useraction',{domain:domain},function(){});
}


function findGroup(obj, id){
    var first_group = $(obj).val();
    $.post('/docs/groups',
        {first_group:first_group},
        function(e){
            var _html = '<select class="col-sm-4" name="sec_group">';
            for(var i in e.result){
                _html += '<option value="'+ e.result[i].name +'">' + e.result[i].name+ '</option>';
            }
            _html += '</select>';
            document.getElementById(id).innerHTML = _html;
        });
}

function secGroup(obj, id){
    var first_group = $(obj).val();
    $.post('/docs/groups',
        {first_group:first_group},
        function(e){
            var _html = '';
            for(var i in e.result){
                _html += '<option value="'+ e.result[i].d_id +'">' + e.result[i].name+ '</option>';
            }
            document.getElementById(id).innerHTML = _html;
        });
}
function queryGroup(obj, id){
    var first_group = $(obj).val();
    $.post('/docs/groups',
        {first_group:first_group},
        function(e){
            var _html = '<option></option>';
            for(var i in e.result){
                _html += '<option value="'+ e.result[i].d_id +'">' + e.result[i].name+ '</option>';
            }
            _html += '</select>';
            document.getElementById(id).innerHTML = _html;
        });
}

function newPageInfo(num){
    var para1 = '';
    var para2 = '';
    var urlpara = window.location.search.replace(/\?/,'').split('&');
    for(i in urlpara)
    {
        if(urlpara[i].indexOf('page=') == 0 ){}
        else{para2 += '&' + urlpara[i];}
    }
    var para1 = '?page=' + num;
    window.location = window.location.pathname + para1 + para2;
}

function stopWxAlarm(event_id){
    var alarm_info = {};
    alarm_info.tags = $('input[name="tags"]:checked').val();
    alarm_info.timeout = $('input[name="timeout"]').val();
    var re = /^[0-9]*[1-9][0-9]*$/ ;
    if(alarm_info.timeout && !re.test(alarm_info.timeout) || alarm_info.timeout > 86400){
        responseTips('rep_tips', '失败: 请输入0-86400之间的整数(默认3600秒)', 'red', 3);
        return;
    }
    alarm_info.origin = $('input[name="origin"]').val();
    alarm_info.alert_attribute = $('input[name="alert_attribute"]').val();
    alarm_info.user = $('input[name="user"]').val();
    $.post('/alarm/stop',
        {
            alarm_info:JSON.stringify(alarm_info)
        },function(e){
            var id = 'tips_' + event_id.split('_')[1];
            if(e.code == 200){
                responseTips(id, '暂停成功', 'green', 2);
            }
            else{
                responseTips(id, '暂停失败', 'red', 2);
            }
            var func = "$('#" + event_id + "').modal('hide')";
            setTimeout(func, 1000);
        });
}

function responseTips(id, tips, color, time){
    if(color === undefined)
        color = 'green';
    if(time === undefined)
        time = 10;
    $('#' + id).show();
    $('#' + id).html(tips).css({'color': color});
    setTimeout( function(){$('#' + id).html(' ');}, ( time * 1000 ) );
}
