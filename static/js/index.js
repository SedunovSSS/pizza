function add2cart(id){
window.location.replace('/add2cart?id=' + id.toString())
}
function del_from_cart(id){
window.location.replace('/del_from_cart?id=' + id.toString())
}
function del_pizza(id){
window.location.replace('/admin/del_pizza?id=' + id.toString())
}
function edit_pizza(id){
window.location.href = '/admin/edit_pizza?id=' + id.toString()
}
function red(url){
    window.location.replace(url)
}
function red_(url){
    window.location.href = url
}