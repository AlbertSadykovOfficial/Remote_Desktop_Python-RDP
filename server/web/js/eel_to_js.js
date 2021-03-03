function send_command(command)
{
		let session_num = document.getElementById('session_num').value;

		if (session_num !== 'sendall')
        eel.solo_command(session_num, command);
    else
    	output('Для данного действия следует выбрать удаленный узел')
}

function read_command()
{
    let session_num = document.getElementById('session_num').value;
    let command = document.getElementById('command').value;

    if (session_num == 'sendall')
        eel.common_command(command)
    else
        eel.solo_command(session_num, command);
}

function open_folder(folder)
{
	let session_num = document.getElementById('session_num').value;
	eel.solo_command(session_num, 'cd ' + folder);
}

eel.expose(output);
function output(data)
{		
		document.getElementById('data').innerHTML = "<ul>" + data + "</ul>";
}

eel.expose(output_catalog);

function output_catalog(data)
{	
		apps = '';
		folders = "<li ondblclick=open_folder('..')><img src='img/folder.png'>..</li>";
		for(i = 0; i < data.length; i++)
		{
				if (data[i].includes('.'))
					apps += "<li oncontextmenu=\"menu('"+data[i]+"'); return false; \">" + data[i].split('.')[0] + ".<span>" + data[i].split('.')[1] + "</span></li>";
				else
					folders += "<li ondblclick=open_folder('"+String(data[i])+"')><img src='img/folder.png'>" + data[i] + "</li>";
		}
		document.getElementById('data').innerHTML = "<ul>" + folders + apps + "</ul>";
}

function download_file(name)
{
		let session_num = document.getElementById('session_num').value;

		if (session_num !== 'sendall')
        eel.solo_command(session_num, 'download ' + name);
    else
    	output('Для данного действия следует выбрать удаленный узел')
}

function menu(name)
{
		if (document.getElementsByClassName('menu').length != 0)
		{
		  	document.getElementsByClassName('menu')[0].remove();
		}

    content = "<div class='menu'>"+
          "<span></span><button class='close_button' onclick=\"document.getElementsByClassName(\'menu\')[0].remove()\"><img src='img/close.png'></button>"+
              "<ul>"+
                  "<li onclick=\"download_file(\'"+name+"\'); document.getElementsByClassName(\'menu\')[0].remove()\">Скачать файл</li>"+
              "</ul>"+
          "</div>";

		document.getElementById('main').insertAdjacentHTML('afterBegin',content);
		document.getElementsByClassName('menu')[0].style = 'margin-left:'+event.pageX+'px; '+'margin-top:'+event.pageY+'px';
}

eel.expose(added_new_node);
function added_new_node(num, ip, meta)
{
    context = "<li id='ul_session_"+num+
			"'><img src='img/green_circle.png'>Session " + num + " --- " + ip + 
			" (" + meta[1] + 
		")</li>";
		document.getElementById('all_nodes').insertAdjacentHTML('beforeEnd', context);
		
		context = "<option id='select_session_"+num+"' value="+num+">"+meta[1]+"</option>";
		document.getElementById('session_num').insertAdjacentHTML('beforeEnd', context);

		for(i = 0; i < meta.length; i++)
		{
				context += "<li>--- " + meta[i] + "</li>";
		}
		document.getElementById('data').innerHTML = '<ul>'+context+'</ul>';
}

eel.expose(delete_node);
function delete_node(num)
{
		document.getElementById('ul_session_'+num).remove();
		document.getElementById('select_session_'+num).remove();
		document.getElementById('data').innerHTML = '';
		document.getElementById('data_header').children[1].style.opacity = '0';
		document.getElementById('data_header').children[0].innerHTML = 'sendall'
}

function change_header(element)
{
		nodes = element.children
		if (element.value !== 'sendall')
		{
				document.getElementById('data_header').children[1].style.opacity = '1';
				for (i=0; i<nodes.length; i++)
				{
					  if (nodes[i].getAttribute('id') == 'select_session_'+element.value)
						 document.getElementById('data_header').children[0].innerHTML = nodes[i].innerHTML;
						console.log(nodes[i].innerHTML)
				}
		} else {
				document.getElementById('data_header').children[1].style.opacity = '0';
				document.getElementById('data_header').children[0].innerHTML = 'sendall'
		}
}