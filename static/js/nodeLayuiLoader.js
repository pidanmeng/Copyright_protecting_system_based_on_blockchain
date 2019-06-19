/**
 * 
 * @authors Your Name (you@example.org)
 * @date    2019-04-28 14:22:43
 * @version $Id$
 */

layui.use(['layer', 'form', 'element', 'laytpl', 'table', 'jquery'], function() {

    {
        var baseUrl = window.location.origin,
            layer = layui.layer,
            form = layui.form,
            element = layui.element,
            tpl = layui.laytpl,
            table = layui.table,
            $ = layui.$ ;

        tpl.config({
            open: '%%',
            close: '%%'
        });
    } //config

    {
        function msg(parameters) {
            var msg = parameters.msg;
            var time = parameters.time;
            layer.msg(msg, { time: time })
        }

        // function openImg(url) {
        //     img = document.createElement('img');
        //     img.src = url;
        //     layer.open({
        //         type: 2,
        //         title: false,
        //         area: [img.width + 'px', img.height + 'px'],
        //         shade: 0.8,
        //         closeBtn: 0,
        //         shadeClose: true,
        //         content: url
        //     });
        // }

        function hasClass(obj, cls) {
            return obj.className.match(new RegExp('(\\s|^)' + cls + '(\\s|$)'));
        }

        var addClass = function(obj, cls) {
            if (!hasClass(obj, cls)) obj.className += " " + cls;
        };

        var removeClass = function(obj, cls) {
            if (hasClass(obj, cls)) {
                var reg = new RegExp('(\\s|^)' + cls + '(\\s|$)');
                obj.className = obj.className.replace(reg, ' ');
            }
        };

        var http = {};

        http.quest = function(option, callback) {
            var url = option.url;
            var method = option.method;
            var data = option.data;
            var timeout = option.timeout || 0;

            var xhr = new XMLHttpRequest();
            (timeout > 0) && (xhr.timeout = timeout);
            xhr.onreadystatechange = function() {
                addClass(document.getElementById('loading'), 'hide');
                var result;
                if (xhr.readyState === 4) {
                    if (xhr.status >= 200 && xhr.status < 400) {
                        result = xhr.responseText;
                        try {
                            result = JSON.parse(xhr.responseText);
                        } catch (e) {
                        }
                        callback && callback(null, result);
                    } else {
                        result = xhr.responseText;
                        try {
                            result = JSON.parse(xhr.responseText);
                        } catch (e) {
                        }
                        callback && callback('status: ' + xhr.status, result);
                    }
                }
            }.bind(this);
            xhr.open(method, url, true);
            if (typeof data === 'object') {
                try {
                    data = JSON.stringify(data);
                } catch (e) {
                    console.log(e)
                }
            }
            removeClass(document.getElementById('loading'), 'hide');
            xhr.send(data);
            xhr.ontimeout = function() {
                callback && callback('timeout', { 'message': '连接超时' });
                msg({msg: '连接超时'});
                console.log('%c连接超时', 'color:red');
            };
        };

        http.get = function(parameters) {
            var url = parameters.url;
            var callback = parameters.callback;
            var timeout = parameters.timeout;
            var option = {};
            option.url = url;
            option.timeout = timeout;
            option.method = 'get';
            this.quest(option, callback);
        };

        http.post = function(parameters) {
            var url = parameters.url;
            var data = parameters.data;
            var callback = parameters.callback;
            var timeout = parameters.timeout;
            var option = {};
            option.url = url;
            option.data = data;
            option.timout = timeout;
            option.method = 'post';
            this.quest(option, callback);
        };

        http.delete = function(parameters) {
            var url = parameters.url;
            var data = parameters.data;
            var callback = parameters.callback;
            var timeout = parameters.timeout;
            var option = {};
            option.url = url;
            option.data = data;
            option.timout = timeout;
            option.method = 'delete';
            this.quest(option, callback);
        };
    } //utilities

    {
        var renderImgLayers = function() {
            $('body').on('click', 'imglayer', function(){
                var img = document.createElement('img');
                img.onload = function(){
                    layer.open({
                        type: 2,
                        title: false,
                        area: [img.width+'px', img.height+'px'],
                        shade: 0.8,
                        closeBtn: 0,
                        skin: 'layui-layer-nobg',
                        shadeClose: true,
                        content: img.src
                    });
                }
                img.src = this.getAttribute('imgurl');
            })
        };
        renderImgLayers();

        var keyHtml = document.getElementById('keys').innerHTML;
        var renderKeys = function(data) {
            (data) || (data = { "publicKey": "null", "privateKey": "null" });
            tpl(keyHtml).render(data, function(html) {
                document.getElementById('keys').innerHTML = html;
            });
        };
        renderKeys();

        var logHtml = document.getElementById('log').innerHTML;
        var renderLog = function(data) {
            (data) || (data = { 'message': '此处会显示一些日志' });
            tpl(logHtml).render(data, function(html) {
                document.getElementById('log').innerHTML = html;
            })
        };
        renderLog();

        var checkerHtml = document.getElementById('checker');
        var renderChecker = function(data) {

            var getTpl = document.getElementById('jtTpl').innerHTML;
            tpl(getTpl).render(data, function(html) {
                checkerHtml.innerHTML = html;
            });
            tpl.config({
                open: '{{',
                close: '}}'
            });
            table.init('jtTables', {});
            tpl.config({
                open: '%%',
                close: '%%'
            });
        };

        var blocksHtml = document.getElementById('blocks');
        var renderBlocks = function() {
            http.get({
                url: baseUrl + '/chain',
                callback: function(err, result) {
                    if (err) {
                        console.log(err);
                        msg({msg: err});
                    } else {
                        var getTpl = document.getElementById('bcTpl').innerHTML;
                        tpl(getTpl).render(result, function(html) {
                            blocksHtml.innerHTML = html;
                        });
                        tpl.config({
                            open: '{{',
                            close: '}}'
                        });
                        table.init('bcTables', {});
                        tpl.config({
                            open: '%%',
                            close: '%%'
                        });
                    }
                }
            });
        };
        renderBlocks();

        var transactionsHtml = document.getElementById('transactions');
        var renderTransactions = function() {
            http.get({
                url: baseUrl + '/transactions',
                callback: function(err, result) {
                    if (err) {
                        console.log(err);
                        msg({msg: err});
                    } else {
                        var getTpl = document.getElementById('otTpl').innerHTML;
                        tpl(getTpl).render(result, function(html) {
                            transactionsHtml.innerHTML = html;
                        });
                        tpl.config({
                            open: '{{',
                            close: '}}'
                        });
                        table.init('otTables', {});
                        tpl.config({
                            open: '%%',
                            close: '%%'
                        });
                    }
                }
            });
        };
        renderTransactions();

        var copyrightsHtml = document.getElementById('copyrights');
        var renderCopyrights = function() {
            http.get({
                url: baseUrl + '/copyright',
                callback: function(err, result) {
                    if (err) {
                        console.log(err);
                        msg({msg: err});
                    } else {
                        var getTpl = document.getElementById('jcTpl').innerHTML;
                        tpl(getTpl).render(result, function(html) {
                            copyrightsHtml.innerHTML = html;
                        });
                        tpl.config({
                            open: '{{',
                            close: '}}'
                        });
                        table.init('jcTables', {});
                        tpl.config({
                            open: '%%',
                            close: '%%'
                        });
                    }
                }
            });
        };

        var nodesHtml = document.getElementById('nodes');
        var renderNodes = function() {
            http.get({
                url: baseUrl + '/node',
                callback: function(err, result) {
                    if (err) {
                        console.log(err);
                        msg({msg: err});
                    } else {
                        var getTpl = document.getElementById('ndTpl').innerHTML;
                        tpl(getTpl).render(result, function(html) {
                            nodesHtml.innerHTML = html;
                        });
                        tpl.config({
                            open: '{{',
                            close: '}}'
                        });
                        table.init('ndTables', {});
                        tpl.config({
                            open: '%%',
                            close: '%%'
                        });
                    }
                }
            });
        };
        renderNodes();
    } //render

    {
        var layid = location.hash.replace(/^#header=/, '');
        element.tabChange('header', layid); //假设当前地址为：http://a.com#test1=222，那么选项卡会自动切换到“发送消息”这一项

        element.on('tab(header)', function() {
            location.hash = 'header=' + this.getAttribute('lay-id');
        });

        element.on('tab(function)', function(data) {
            if (data.index === 3) {
                renderCopyrights();
            }
        });
    } //tab


    {

        form.on('submit(createKey)', function() {
            http.post({
                url: baseUrl + '/user',
                data: null,
                callback: function(err, result) {
                    if (err) {
                        console.log(err);
                        msg({msg: err});
                    } else {
                        renderKeys(result);
                    }
                    renderLog(result);
                }
            });
            return false; //阻止表单跳转。如果需要表单跳转，去掉这段即可。
        });

        form.on('submit(loadKey)', function() {
            http.get({
                url: baseUrl + '/user',
                callback: function(err, result) {
                    if (err) {
                        console.log(err);
                        msg({msg: err});
                    } else {
                        renderKeys(result);
                    }
                    renderLog(result);
                }
            });
            return false;
        });

        form.on('submit(addTransaction)', function(data) {
            var postData = { "picUrl": data.field.addTransaction };
            http.post({
                url: baseUrl + '/transaction',
                data: postData,
                callback: function(err, result) {
                    if (err) {
                        msg({msg: err});
                    } else {
                        renderTransactions();
                    }
                    renderLog(result);
                }
            });
            return false;
        });

        form.on('submit(checkTort)', function(data) {
            var urls = data.field.checkTort.split('\n');
            var postData = { "urls": urls };
            http.post({
                url: baseUrl + '/tort',
                data: postData,
                callback: function(err, result) {
                    if (err) {
                        console.log(err);
                        msg({msg: err});
                    } else {
                        renderChecker(result);
                        $('#jt').click();
                    }
                    renderLog(result);
                }
            });
            return false;
        });

        form.on('submit(mine)', function() {
            http.post({
                url: baseUrl + '/mine',
                callback: function(err, result) {
                    if (err) {
                        console.log(err);
                        msg({msg: err});
                    } else {
                        renderBlocks();
                        renderTransactions();
                    }
                    renderLog(result);
                }
            });
            return false;
        });

        form.on('submit(resolve)', function() {
            http.post({
                url: baseUrl + '/resolveConflicts',
                callback: function(err, result) {
                    if (err) {
                        console.log(err);
                        msg({msg: err});
                    } else {
                        renderBlocks();
                        renderTransactions();
                    }
                    renderLog(result);
                }
            });
            return false;
        });

        form.on('submit(addNode)', function(data) {
            var node = data.field.node;
            var postData = { "node": node };
            http.post({
                url: baseUrl + '/node',
                data: postData,
                callback: function(err, result) {
                    if (err) {
                        console.log(err);
                        msg({msg: err});
                    } else {
                        renderNodes();
                    }
                    console.log(result);
                    renderLog(result);
                }
            });
            return false;
        });

        form.on('submit(removeNode)', function(data) {
            var node = data.field.node;
            var postData = { "node": node };
            http.delete({
                url: baseUrl + '/node/' + node,
                data: postData,
                callback: function(err, result) {
                    if (err) {
                        console.log(err);
                        msg({msg: err});
                    } else {
                        renderNodes();
                    }
                    console.log(result);
                    renderLog(result);
                }
            });
            return false;
        });
    } //listener

    document.getElementById('loadKey').click();
    renderCopyrights();
});