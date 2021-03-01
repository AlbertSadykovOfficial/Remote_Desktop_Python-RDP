 function read_command()
{
    let session_num = document.getElementById('session_num').value;
    let command = document.getElementById('command').value;

    if (session_num == 'sendall')
        eel.common_command(command)
    else
        eel.solo_command(session_num, command);
}

eel.expose(output);
function output(data)
{		
		document.getElementById('data').innerHTML = '<h1>'+data+'</h1>';
}

eel.expose(output_catalog);
function output_catalog(data)
{	
		context = '';
		for(i = 0; i < data.length; i++)
		{
				if (data[i].includes('.'))
					context += "<li>" + data[i] + "</li>";
				else
					context += "<li><img src='img/folder.png'>" + data[i] + "</li>";
		}
		document.getElementById('data').innerHTML = "<ul>" + context + "</ul>";
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