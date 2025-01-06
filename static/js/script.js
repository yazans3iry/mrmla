const productSelect = document.getElementById('product_select');
const unitSpan = document.getElementById('unit');
const priceSpan = document.getElementById('price');
const priceInput = document.getElementById('price_input'); // الحقل المخفي

productSelect.addEventListener('change', function() {
    const selectedOption = this.options[this.selectedIndex];
    unitSpan.textContent = selectedOption.getAttribute('data-unit');
    priceSpan.textContent = selectedOption.getAttribute('data-price');
    
    // تحديث حقل السعر المخفي
    priceInput.value = selectedOption.getAttribute('data-price');
});
