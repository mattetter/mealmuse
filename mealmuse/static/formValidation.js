// function validateForm() {
//     let daysSelect = document.getElementById('days');
//     let dietSelect = document.getElementById('diet');
    
//     if (getSelectedOptions(daysSelect).length === 0 || getSelectedOptions(dietSelect).length === 0) {
//         alert('Please select at least one day and one dietary preference.');
//         return false;
//     }
//     return true;
// }

// function getSelectedOptions(select) {
//     let result = [];
//     let options = select && select.options;
//     let opt;

//     for (let i = 0, iLen = options.length; i < iLen; i++) {
//         opt = options[i];

//         if (opt.selected) {
//             result.push(opt.value || opt.text);
//         }
//     }
//     return result;
// }

// function handleDietaryPreferenceChange(select) {
//     const noRestrictionsOption = select.querySelector('option[value="No Restrictions"]');
    
//     if (getSelectedOptions(select).length > 1 && noRestrictionsOption.selected) {
//         noRestrictionsOption.selected = false;
//     }
// }
