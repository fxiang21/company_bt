/**
 * Created by xiangfeng on 15/11/8.
 */
function docQuery(){
    var first_group = $('#first_group_query').val();
    var sec_group = $('#sec_group_query').val();
    var doc_title = $('#doc_title_query').val();
    var doc_keys = $('#doc_keys_query').val();
    var url = '/docs?first_group=' + first_group;
    url += '&sec_group=' + sec_group;
    url += '&doc_title=' + doc_title;
    url += '&doc_keys=' + doc_keys;
    window.location = url;
}

function docDeleteTips(d_id){
    var func = 'docDelete("' + d_id + '")';
    $('#doc_delete_sure').attr('onclick',func);
    $('#doc_delete').modal('show');
}

function docDelete(id){;
    $.post('/docs/delete',
            {d_id:id},
            function(e){
                window.history.go(0);
            });
}

function docUpdateTips(d_id){
    var func = 'docUpdate("' + d_id + '")';
    $('#doc_update_sure').attr('onclick',func);
    $('#doc_update').modal('show');
    $.post('/docs/info',{d_id:d_id},function(e){
        console.log(e.result);
        $('#doc_title_update').val(e.result.title);
        $('#doc_comment_update').val(e.result.comment);
        $('#doc_keys_update').val(e.result.keys);
        $('#doc_update_id').attr('value', d_id);
        $('#update_doc_md5').val(e.result.doc_md5);
        $('#update_first_group').val(e.first_group);
        var _html = '';
        console.log(e.sec_groups);
        for(var i in e.sec_groups){
            console.log(e.sec_groups[i]);
            _html += '<option value="'+ e.sec_groups[i].id +'">' + e.sec_groups[i].name + '</option>';
        }
        document.getElementById('update_sec_group').innerHTML = _html;
        $('#update_sec_group').val(e.result.group_id);
    });
}

function docUpdate(id){
    var doc_keys = $('#doc_keys_update').val();
    var doc_comment = $('#doc_comment_update').val();
    var update_sec_group = $('#update_sec_group').val();
    var doc_title_update = $('#doc_title_update').val();
    var update_doc_md5 = $('#update_doc_md5').val();
    $.post('/docs/update',
            {
                keys:doc_keys,
                comment:doc_comment,
                update_doc_md5:update_doc_md5,
                update_sec_group:update_sec_group,
                doc_title_update:doc_title_update
            },
            function(e){
                if(e.code == 202){
                    responseTips('doc_update_tips', '标题已经存在,请重新输入', 'red', 3);
                }
                else if(e.code == 500){
                    responseTips('doc_update_tips', '失败:服务器错误', 'red', 3);
                }
                else{
                    window.history.go(0);
                }
            });
}

function docUpgradeTips(id){
    $.post('/docs/info',
            {
                d_id:id
            },
            function(e){
                $('#doc_title_upgrade').val(e.result.title);
                $('#doc_comment_upgrade').val(e.result.comment);
                $('#doc_keys_upgrade').val(e.result.keys);
                $('#group_id_upgrade').attr('value', e.result.group_id);
    });
    $('#doc_upgrade').modal('show');
}

function doc_edit_check(){
    var d_id = $('#doc_id').val();
    var doc_md5 = $('#doc_md5').val();
    var sec_group = $('#sec_group').val();
    if(!sec_group){
        responseTips('sec_group_tips', '分类不能为空，如果没有备选项，请先创建分类', 'red', '3');
        return false;
    }
    var return_code = false;
    $.ajax({
      type: 'POST',
      url: '/docs/is_new',
      data: {d_id:d_id, doc_md5:doc_md5},
      success: function(resp){
                    if(!resp.exist_update){
                        return_code = true;
                    }
                    else{
                        responseTips('commit_tips', '当前文档内容已不是最新版本，建议备份您的更改，并刷新页面再次更新', 'red', 5);
                        return_code = false;
                    }
                },
      async:false
    });
    return return_code
}

function inputGroup(){
    var first_group = $('#new_first_group').val();
    var sec_group = $('#new_sec_group').val();
    $.post('/docs/sec_groups/add',
        {
            first_group:first_group,
            sec_group:sec_group
        },function(resp){
            if(!resp.status){
                responseTips('new_group_input_tips', '添加失败', 'red', 3);
            }
            else{
                window.history.go(0);
            }
        });
}