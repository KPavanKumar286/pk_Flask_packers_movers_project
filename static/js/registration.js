function togglePassword(id){
    const password = document.getElementById(id)
    password.type = password.type === 'password' ? 'text' : 'password' ;
}