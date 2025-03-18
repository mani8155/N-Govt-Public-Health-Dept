// 2. Whether the students of the institution were already permitted for the practical training in PHC. If so copies enclosed.
// document.addEventListener("DOMContentLoaded", function () {
//     let permittedSelect = document.getElementById("permitted_select");
//     let permittedFields = document.getElementById("permitted_fields");
//     let go1 = document.querySelector("input[name='permitted_in_phc_gov_no']");
//     let go2 = document.querySelector("input[name='permitted_in_phc_gov_date']");
//     let go3 = document.querySelector("input[name='permitted_in_phc_upload_uid']");
//     let go4 = document.getElementById("permitted_in_phc_upload_uid_hide");
//     let existingFile = go4.value;
//
//     function toggleFields() {
//         if (permittedSelect.value === "yes") {
//             permittedFields.style.display = "flex"; // Show the fields
//             go1.setAttribute("required", "required");
//             go2.setAttribute("required", "required");
//
//             // Check if a file is already selected, and only make it required if no file exists
//             if (existingFile) {
//
//                 go3.setAttribute("required", "required"); // Only required if no file exists
//             } else {
//
//                 go3.removeAttribute("required"); // If file exists, make file input not required
//             }
//         } else {
//             permittedFields.style.display = "none"; // Hide the fields
//             go1.removeAttribute("required");
//             go2.removeAttribute("required");
//             go3.removeAttribute("required");
//             // Remove the required attribute from file input
//         }
//     }
//
//    toggleFields();
//
//     // Dropdown change
//     permittedSelect.addEventListener("change", toggleFields);
//
//     // Also run when file input changes (user selects a file)
//     go3.addEventListener("change", toggleFields);
// });
//


document.addEventListener("DOMContentLoaded", function () {
    let permittedSelect = document.getElementById("permitted_select");
    let permittedFields = document.getElementById("permitted_fields");
    let go1 = document.querySelector("input[name='permitted_in_phc_gov_no']");
    let go2 = document.querySelector("input[name='permitted_in_phc_gov_date']");
    let go3 = document.querySelector("input[name='permitted_in_phc_upload_uid']");
    let go4 = document.getElementById("permitted_in_phc_upload_uid_hide");

    function toggleFields() {
        if (permittedSelect.value === "yes") {
            permittedFields.style.display = "flex";
            go1.setAttribute("required", "required");
            go2.setAttribute("required", "required");

            const hasExistingFile = go4 && go4.value.trim() !== "";
            const hasNewFile = go3 && go3.files && go3.files.length > 0;

            if (!hasExistingFile && !hasNewFile) {
                go3.setAttribute("required", "required");
            } else {
                go3.removeAttribute("required");
            }
        } else {
            permittedFields.style.display = "none";
            go1.removeAttribute("required");
            go2.removeAttribute("required");
            go3.removeAttribute("required");
        }
    }

    // Initial call on page load
    toggleFields();

    // When dropdown value changes
    permittedSelect.addEventListener("change", function () {
        toggleFields();
    });

    // Also trigger check when file input changes
    go3.addEventListener("change", function () {
        toggleFields();
    });
});





// 3. Continuance of provisional affiliation granted by the Tamil Nadu MGR Medical University
document.addEventListener("DOMContentLoaded", function () {
    // Call the reusable function for both dropdowns
    populateAcademicYearOptions("academic_year_input", "academic_year_select");
    populateAcademicYearOptions("academic_year_input", "academic_year_select2");
    populateAcademicYearOptions("academic_year_input", "academic_year_select3");
    populateAcademicYearOptions("academic_year_input", "academic_year_select4");
    populateAcademicYearOptions("academic_year_input", "academic_year_select5");
});

function populateAcademicYearOptions(inputId, selectId) {
    let inputField = document.getElementById(inputId);
    let selectField = document.getElementById(selectId);

    if (inputField && selectField) {
        let currentYear = inputField.value.trim();

        if (currentYear.includes("-")) {
            let years = currentYear.split("-");
            let startYear = parseInt(years[0].trim(), 10);
            let endYear = parseInt(years[1].trim(), 10);

            if (!isNaN(startYear) && !isNaN(endYear)) {
                let previousStartYear = startYear - 1;
                let previousEndYear = endYear - 1;

                let optionsToAdd = [
                    `${startYear}-${endYear}`,
                    `${previousStartYear}-${previousEndYear}`
                ];

                optionsToAdd.forEach(year => {
                    let exists = [...selectField.options].some(option => option.value === year);
                    if (!exists) {
                        let newOption = document.createElement("option");
                        newOption.value = year;
                        newOption.textContent = year;
                        selectField.appendChild(newOption);
                    }
                });
            }
        }
    }
}
