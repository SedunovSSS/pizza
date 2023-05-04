var maestro = [50, 56, 57, 58, 63, 67];
var mastercard = [51, 52, 53, 54, 55];
var diners = [36, 30, 38];
var jcb = [31, 35];
var ae = [34, 37];

function changeCard(){
    var str = document.getElementById('card').value.toString();
    while (str.length < 16){
        str += '0';
    }
    document.getElementById('image-card').innerHTML = str;
    if (str.substring(0, 1) == '4'){
        document.getElementById('op-card').innerHTML = 'VISA';
    }
    else if (str.substring(0, 1) == '2'){
        document.getElementById('op-card').innerHTML = 'MIR';
    }
    else if (str.substring(0, 2) == '60'){
        document.getElementById('op-card').innerHTML = 'DISCOVER';
    }
    else if (str.substring(0, 2) == '62'){
        document.getElementById('op-card').innerHTML = 'China UnionPay';
    }
    else if (str.substring(0, 1) == '7'){
        document.getElementById('op-card').innerHTML = 'UEK';
    }
    else if (maestro.includes(Number(str.substring(0, 2)))){
        document.getElementById('op-card').innerHTML = 'MAESTRO';
    }
    else if (mastercard.includes(Number(str.substring(0, 2)))){
        document.getElementById('op-card').innerHTML = 'MASTERCARD';
    }
    else if (diners.includes(Number(str.substring(0, 2)))){
        document.getElementById('op-card').innerHTML = 'DINERS';
    }
    else if (jcb.includes(Number(str.substring(0, 2)))){
        document.getElementById('op-card').innerHTML = 'JCB International';
    }
    else if (ae.includes(Number(str.substring(0, 2)))){
        document.getElementById('op-card').innerHTML = 'American Express';
    }
    else{
        document.getElementById('op-card').innerHTML = 'NONE';
    }
}
function changeCVV(){
    var str = document.getElementById('cvv').value.toString();
    while (str.length < 3){
        str += '0';
    }
    document.getElementById('image-cvv').innerHTML = str;
}