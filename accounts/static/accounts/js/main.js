var labels = document.getElementsByTagName('label');
var inputs = document.getElementsByTagName('input');
var selects = document.getElementsByTagName('select');
var parent;

for (label of labels){
    label.classList.add('form-label');
    label.classList.add('color-white');
    parent = label.parentNode;
    parent.classList.add('mb-3');

}


for (input of inputs){
    input.classList.add('form-control');
    parent = input.parentNode;
    parent.classList.add('mb-3');
}

for (select of selects){
    select.classList.add('form-select');
    parent = select.parentNode;
    parent.classList.add('mb-3');
}