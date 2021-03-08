function create_file()
{
  	send_command('create_file ' + document.getElementById('menu_input').value)
  	document.getElementsByClassName('menu')[0].remove();
}

function create_folder()
{
  	send_command('create_folder ' + document.getElementById('menu_input').value)
  	document.getElementsByClassName('menu')[0].remove();
}
function rename()
{
    //send_command('rename ' + document.getElementById('hidden_input').value + ' ' + document.getElementById('menu_input').value)
    console.log('rename ' + document.getElementById('hidden_input').value + ' ' + document.getElementById('menu_input').value)
}

function form(action, value)
{
		document.getElementsByClassName('menu')[0].remove();
    content = "<div class='menu'>"+
          "<span></span><button class='close_button' onclick=\"document.getElementsByClassName(\'menu\')[0].remove()\"><img src='img/close.png'></button>"+
              "<ul>"+
                  "<li>Название</li>"+
                  "<input id='hidden_input' type='text' style='display:none' value='"+value+"'>"+
                  "<li><input id='menu_input' type='text'></li>"+
                  "<li><button onclick='" + action + "()'>Ok</button></li>"+
              "</ul>"+
          "</div>";
    document.getElementsByTagName('body')[0].insertAdjacentHTML('afterBegin', content);
    console.log(event.pageX, event.pageY);
		document.getElementsByClassName('menu')[0].style = 'margin-left:' + event.pageX + 'px; ' + 'margin-top:' + event.pageY + 'px;';

}

function manipulate(action, name)
{
    let session_num = document.getElementById('session_num').value;

    if (session_num !== 'sendall')
        eel.solo_command(session_num, action + ' ' + name);
    else
        output('Для данного действия следует выбрать удаленный узел')
}

function menu(object, name)
{
    if (document.getElementsByClassName('menu').length != 0)
    {
        document.getElementsByClassName('menu')[0].remove();
    }

    content = "<div class='menu'>"+
          "<span></span><button class='close_button' onclick=\"document.getElementsByClassName(\'menu\')[0].remove()\"><img src='img/close.png'></button>"+
              "<ul>"+
                  "<li onclick=\"manipulate('download',\'"+name+"\'); document.getElementsByClassName(\'menu\')[0].remove()\">Скачать</li>"+
                  "<li onclick=\"manipulate('delete_"+object+"',\'"+name+"\');\">Удалить</li>"+
                  "<li onclick=\"form('create_file','');\">Создать файл</li>"+
                  "<li onclick=\"form('create_folder','');\">Создать папку</li>"+
                  "<li onclick=\"form('rename','" + name + "');\">Переименовать</li>"+
              "</ul>"+
          "</div>";

    document.getElementsByTagName('body')[0].insertAdjacentHTML('afterBegin', content);
    console.log(event.pageX, event.pageY);
    document.getElementsByClassName('menu')[0].style = 'margin-left:' + event.pageX + 'px; ' + 'margin-top:' + event.pageY + 'px;';
}