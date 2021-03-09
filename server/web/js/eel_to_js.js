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
        eel.common_command(session_num + ' ' + command)
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
		for(i = 0; i < JSON.parse(data)[0].length; i++)
		{
						folders += "<li oncontextmenu=\"menu('folder', '" + JSON.parse(data)[0][i] + "'); return false\" " + 
														" ondblclick=\"open_folder('"+ JSON.parse(data)[0][i] +"')\">" + 
														"<img src='img/folder.png'>" + JSON.parse(data)[0][i] + 
											"</li>";
		}
		for(i = 0; i < JSON.parse(data)[1].length; i++)
		{
				if (JSON.parse(data)[1][i].includes('.'))
						apps += "<li oncontextmenu=\"menu('file', '"+JSON.parse(data)[1][i]+"'); return false; \">" + 
												JSON.parse(data)[1][i].split('.')[0] + 
												".<span>" + JSON.parse(data)[1][i].split('.')[1] + "</span>" + 
										"</li>";
				else
						apps += "<li oncontextmenu=\"menu('file', '"+JSON.parse(data)[1][i]+"'); return false; \">" + 
												JSON.parse(data)[1][i].split('.')[0] + 
										"</li>";
		}
		document.getElementById('data').innerHTML = "<ul>" + folders + apps + "</ul>";
}

eel.expose(added_new_node);
function added_new_node(num, ip, meta)
{
	// meta[4] - Сететвое имя компьютера в  пришедшем списке
    context = "<li id='ul_session_" + num + "'>"+
    							"<img src='img/green_circle.png'>" + 
									"Session " + num + " --- " + ip + 
									" (" + meta[4] + ")" +
							"</li>";
		document.getElementById('all_nodes').insertAdjacentHTML('beforeEnd', context);
		
		context = "<option id='select_session_"+num+"' value="+num+">"+meta[4]+"</option>";
		document.getElementById('session_num').insertAdjacentHTML('beforeEnd', context);

		print_list_to_html(meta);
}

eel.expose(print_list_to_html)
function print_list_to_html(meta)
{			
		context = '';
		for(i = 0; i < meta.length; i++)
		{
				context += "<li> " + meta[i] + "</li>";
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
		document.getElementById('data_header').children[0].innerHTML = 'sendall';
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
				}
		} else {
				document.getElementById('data_header').children[1].style.opacity = '0';
				document.getElementById('data_header').children[0].innerHTML = 'sendall';
		}
}

eel.expose(alert_message);
function alert_message(message)
{
		alert(message);
}

function close_program()
{
		eel.common_command('exit');
		window.open('close.html', '_self').close();
}

/*

eel.expose(output_catalog);
function output_catalog(data)
{	
		apps = '';
		folders = "<li ondblclick=open_folder('..')><img src='img/folder.png'>..</li>";
		for(i = 0; i < data.length; i++)
		{
				if (data[i].includes('.'))
						apps += "<li oncontextmenu=\"menu('file', '"+data[i]+"'); return false; \">" + data[i].split('.')[0] + ".<span>" + data[i].split('.')[1] + "</span></li>";
				else
						folders += "<li oncontextmenu=\"menu('folder', '"+data[i]+"'); return false\" ondblclick=\"open_folder('"+data[i]+"')\"><img src='img/folder.png'>" + data[i] + "</li>";
		}
		document.getElementById('data').innerHTML = "<ul>" + folders + apps + "</ul>";
}


*/