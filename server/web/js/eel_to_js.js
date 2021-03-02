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
					apps += "<li>" + data[i].split('.')[0] + ".<span>" + data[i].split('.')[1] + "</span></li>";
				else
					folders += "<li ondblclick=open_folder('"+String(data[i])+"')><img src='img/folder.png'>" + data[i] + "</li>";
		}
		document.getElementById('data').innerHTML = "<ul>" + folders + apps + "</ul>";
}
eel.expose(added_new_node);
function added_new_node(num, ip, meta)
{
    context = "<li id='ul_session_"+num+
			"'><img src='img/green_circle.png'>Session " + num + " --- " + ip + 
			" (" + meta[1] + 
		")</li>";

		document.getElementById('all_nodes').insertAdjacentHTML('beforeEnd', context);
		
		context = "<option id='ul_session_"+num+"' value="+num+">"+meta[1]+"</option>";
		document.getElementById('session_num').insertAdjacentHTML('beforeEnd', context);

		for(i = 0; i < meta.length; i++)
		{
				context += "<li>--- " + meta[i] + "</li>";
		}
		document.getElementById('data').innerHTML = '<ul>'+context+'</ul>';
}

function change_header(element)
{
		nodes = element.children
		if (element.value !== 'sendall')
		{
				document.getElementById('data_header').children[1].style.opacity = '1';
				for (i=0; i<nodes.length; i++)
				{
					  if (nodes[i].getAttribute('id') == 'ul_session_'+element.value)
						 document.getElementById('data_header').children[0].innerHTML = nodes[i].innerHTML;
						console.log(nodes[i].innerHTML)
				}
		} else {
				document.getElementById('data_header').children[1].style.opacity = '0';
				document.getElementById('data_header').children[0].innerHTML = 'sendall'
		}
}