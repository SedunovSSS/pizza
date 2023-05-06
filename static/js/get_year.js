var dateObj = new Date();
var year = dateObj.getUTCFullYear().toString();
if (year == '2023'){year = ''}
else{ year = '-' + year}
document.getElementById('pizza_h1').innerHTML = 'Пицца &copy; 2023' + year + ' Все права защищены';