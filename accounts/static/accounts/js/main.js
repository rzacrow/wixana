var labels = document.getElementsByTagName('label');
var inputs = document.getElementsByTagName('input');
var selects = document.getElementsByTagName('select');
var parent;
var radioes = document.getElementsByName('response');

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

for (radio of radioes){
    radio.classList.add('form-check-input');
    parent = radio.parentNode;
    parent.classList.remove('mb-3');
    parent.classList.add('form-check-label');

    var second_parent = parent.parentNode;
    second_parent.classList.remove('mb-3');
    second_parent.classList.add('col-12');
}