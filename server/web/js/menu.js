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

function create(value)
{
		document.getElementsByClassName('menu')[0].remove();
    content = "<div class='menu'>"+
          "<span></span><button class='close_button' onclick=\"document.getElementsByClassName(\'menu\')[0].remove()\"><img src='img/close.png'></button>"+
              "<ul>"+
                  "<li>Название</li>"+
                  "<li><input id='menu_input' type='text'></li>"+
                  "<li><button onclick='create_"+value+"()'>Ok</button></li>"+
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
                  "<li onclick=\"create('file');\">Создать файл</li>"+
                  "<li onclick=\"create('folder');\">Создать папку</li>"+
              "</ul>"+
          "</div>";

    document.getElementsByTagName('body')[0].insertAdjacentHTML('afterBegin', content);
    console.log(event.pageX, event.pageY);
    document.getElementsByClassName('menu')[0].style = 'margin-left:' + event.pageX + 'px; ' + 'margin-top:' + event.pageY + 'px;';
}