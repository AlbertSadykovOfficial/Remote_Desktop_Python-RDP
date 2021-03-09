function remove_menu()
{
  document.getElementsByClassName('menu')[0].remove();
}

function create_file()
{
  	send_command('create_file ' + document.getElementById('menu_input').value)
  	remove_menu();
}

function create_folder()
{
  	send_command('create_folder ' + document.getElementById('menu_input').value)
  	remove_menu();
}
function rename()
{
    send_command('rename=>' + document.getElementById('hidden_input').value + ' | ' + document.getElementById('menu_input').value);
    remove_menu();
}

function form(action, value)
{
		remove_menu();
    content = 
          "<div class='menu'>"+
              "<span></span><button class='close_button' onclick=\"remove_menu()\"><img src='img/close.png'></button>"+
              "<ul>"+
                  "<li>Название</li>"+
                  "<input id='hidden_input' type='text' style='display:none' value='"+value+"'>"+
                  "<li><input id='menu_input' type='text'></li>"+
                  "<button class='green_button' style='margin-top: 5px;' onclick='" + action + "();'>Apply</button>"+
              "</ul>"+
          "</div>";
    document.getElementsByTagName('body')[0].insertAdjacentHTML('afterBegin', content);
		document.getElementsByClassName('menu')[0].style = 'margin-left:' + event.pageX + 'px; ' + 'margin-top:' + event.pageY + 'px;';

}

function manipulate(action, name)
{
    let session_num = document.getElementById('session_num').value;

    if (session_num !== 'sendall')
        eel.solo_command(session_num, action + ' ' + name);
    else
        output('Для данного действия следует выбрать удаленный узел')

     remove_menu();
}

function menu(object, name)
{
    if (document.getElementsByClassName('menu').length != 0)
    {
        document.getElementsByClassName('menu')[0].remove();
    }

    content = "<div class='menu'>"+
          "<span></span><button class='close_button' onclick='remove_menu()'><img src='img/close.png'></button>"+
              "<ul>"+
                  "<li onclick=\"manipulate('download_"+object+"',\'"+name+"\');\">Скачать</li>"+
                  "<li onclick=\"manipulate('delete_"+object+"',\'"+name+"\');\">Удалить</li>"+
                  "<li onclick=\"form('create_file','');\">Создать файл</li>"+
                  "<li onclick=\"form('create_folder','');\">Создать папку</li>"+
                  "<li onclick=\"form('rename','" + name + "');\">Переименовать</li>"+
              "</ul>"+
          "</div>";

    document.getElementsByTagName('body')[0].insertAdjacentHTML('afterBegin', content);
    document.getElementsByClassName('menu')[0].style = 'margin-left:' + event.pageX + 'px; ' + 'margin-top:' + event.pageY + 'px;';
}