const themeToggle = document.createElement('button');
themeToggle.innerText = '🌓 Theme';
themeToggle.onclick = () => {
    const theme = document.body.classList.contains('dark') ? 'light' : 'dark';
    document.body.className = theme;
    localStorage.setItem('theme', theme);
};
document.body.prepend(themeToggle);
if (localStorage.getItem('theme') === 'dark') document.body.classList.add('dark');
