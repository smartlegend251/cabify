var sidebar = document.getElementById('sidebar');
    var menuToggle = document.getElementById('menu-toggle');
    
    menuToggle.addEventListener('click', function() {
      if (sidebar.style.left === '-100%') {
        if (sidebar.style.left > '13%' && sidebar.style.left < '0%'){
            sidebar.style.display = 'hide'
        }
        else{
            // sidebar.style.display = 'block'
        }
        sidebar.style.left = '0%';
      } else {
        sidebar.style.left = '-100%';
      }
    });