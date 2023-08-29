
// function showSelectedDays() {
//     const checkboxes = document.querySelectorAll("#selectDaysForm input[type='checkbox']:checked");
//     const cardsContainer = document.getElementById('cardsContainer');
//     const daysFormContainer = document.getElementById('daysForm');
  
//     // Retrieve family size from the globalFamilySize dropdown
//     const familySizeDropdown = document.getElementById('FamilySize');
//     const familySize = familySizeDropdown.value;
  
//     if (checkboxes.length === 0) {
//         alert("Please select at least one day");
//         return;
//     }
  
//     document.getElementById('selectDaysForm').style.display = 'none';
//     daysFormContainer.style.height = 'auto';
  
//     checkboxes.forEach(checkbox => {
        
//       const card = document.createElement('div');
//       card.className = 'card m-2';
  
//       card.innerHTML = `
//           <div class="card-body">
//               <h3 class="card-title">${checkbox.value}</h3>
//               <div class="form-group">
//                   <label><input type="checkbox" class="mr-1" value="Breakfast"> Breakfast</label>
//                   <label class="ml-2"><input type="checkbox" class="mr-1" value="Lunch"> Lunch</label>
//                   <label class="ml-2"><input type="checkbox" class="mr-1" value="Dinner" checked> Dinner</label>
//                   <label class="ml-2"><input type="checkbox" class="mr-1" value="Snack"> Snack</label>
//                   <label class="ml-2"><input type="checkbox" class="mr-1" value="Dessert"> Dessert</label>
//               </div>
//               <div class="form-group">
//                   <label for="${checkbox.value}-time">Time available to cook:</label>
//                   <select id="${checkbox.value}-time" class="form-control" style="width: auto;">
//                       <option value="0">no time</option>
//                       <option value="15" selected>15 mins</option>
//                       <option value="30">30 mins</option>
//                       <option value="60">1 hour</option>
//                         <option value="120">2 hours</option>
//                         <option value="240">4 hours</option>
//                         <option value="800">unlimited</option>

//                   </select>
//               </div>
//               <div class="form-group">
//                   <label for="${checkbox.value}-people">Cooking for:</label>
//                   <select id="${checkbox.value}-people" class="form-control" style="width: auto;">
//                       <option value="1" selected>1 person</option>
//                       <option value="2">2 people</option>
//                       <option value="3">3 people</option>
//                       <option value="4">4 people</option>
//                       <option value="5">5 people</option>
//                       <option value="6">6 people</option>
//                       <option value="7">7 people</option>
//                       <option value="8">8 people</option>
//                       <option value="9">9+ people</option>
//                   </select>
//               </div>
//               <div class="form-group">
//                   <label for="${checkbox.value}-cuisine">Cuisine/Requests:</label>
//                   <input type="text" id="${checkbox.value}-cuisine" class="form-control" placeholder="E.g. Italian, Low Carb">
//               </div>
//           </div>
//       `;
  
//       cardsContainer.appendChild(card);
  
//       // Set the selected value of the dropdown to the family size value
//       const selectElem = document.getElementById(`${checkbox.value}-people`);
//       selectElem.value = familySize;
//     });
  
//     document.getElementById('cardsForm').style.display = 'block';
  
//     // Attach the event listener
//     attachCardsFormEventListener();
//   }
  
//   function attachCardsFormEventListener() {
//     // Ensure that the event listener is only attached once
//     const form = document.getElementById('cardsForm');
//     if (form.getAttribute('data-listener') !== 'true') {
//         form.addEventListener('submit', handleFormSubmit);
//         form.setAttribute('data-listener', 'true');
//     }
//   }
  
//   function handleFormSubmit(event) {
//     event.preventDefault(); // prevent default form submission behavior
  
//     let formData = new FormData();
  
//     const cards = document.querySelectorAll("#cardsContainer .card");
  
//     cards.forEach(card => {
//         const day = card.querySelector('.card-title').textContent;
//         const meals = Array.from(card.querySelectorAll("input[type='checkbox']:checked"))
//                       .map(input => input.value);
//         const timeToCook = card.querySelector('select[id$="-time"]').value;
//         const cookingFor = card.querySelector('select[id$="-people"]').value;
//         const cuisine = card.querySelector('input[id$="-cuisine"]').value;
  
//         formData.append(day, JSON.stringify({
//             meals: meals,
//             timeToCook: timeToCook,
//             cookingFor: cookingFor,
//             cuisine: cuisine
//         }));
//     });
  
//     fetch("/process_meal_plan", {
//         method: "POST",
//         body: formData
//     })
//     .then(response => response.json())
//     .then(data => {
//         if (data.success) {
//             location.reload();
//         } else {
//             alert('Error processing meal plan');
//         }
//     });
//   }
  
  
//   // Originally, you were attaching the event listener outside any function. 
//   // This would attach the event listener as soon as the script runs.
//   // Now, we've removed that, and the event listener gets attached inside the showSelectedDays function.
  