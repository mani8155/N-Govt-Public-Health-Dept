// Course Application ID
function applicationIdGenerateFunction(selectElement) {
    let course = selectElement.value;
    $.ajax({
        url: applicationIdUrl,
        data: { course_id: course },
        success: function (data) {

            document.getElementById('document_id').value = data.application_id;
        },
        error: function (error) {
            console.error("Error:", error);
        }
    });
}



// 2. Whether the students of the institution were already permitted for the practical training in PHC. If so copies enclosed.
document.getElementById("permitted_select").addEventListener("change", function() {
    var permittedFields = document.getElementById("permitted_fields");
    var go1 = document.querySelector("input[name='permitted_in_phc_gov_no']");
    var go2 = document.querySelector("input[name='permitted_in_phc_gov_date']");
    var go3 = document.querySelector("input[name='permitted_in_phc_upload_uid']");

    if (this.value === "yes") {
        permittedFields.style.display = "flex"; // Show fields
        go1.setAttribute("required", "required");
        go2.setAttribute("required", "required");
        go3.setAttribute("required", "required");
    } else {
        permittedFields.style.display = "none"; // Hide fields
        go1.removeAttribute("required");
        go2.removeAttribute("required");
        go3.removeAttribute("required");
    }
});



// 3. Continuance of provisional affiliation granted by the Tamil Nadu MGR Medical University
document.addEventListener("DOMContentLoaded", function () {
    function populateAcademicYearOptions(inputFieldId, selectFieldId) {
        let inputField = document.getElementById(inputFieldId);
        let selectField = document.getElementById(selectFieldId);

        if (inputField && selectField) {
            let currentYear = inputField.value.trim();

            if (currentYear.includes("-")) {
                let [start, end] = currentYear.split("-").map(year => parseInt(year.trim(), 10));

                if (!isNaN(start) && !isNaN(end)) {
                    let options = [
                        `${start}-${end}`,
                        `${start - 1}-${end - 1}`
                    ];

                    options.forEach(opt => {
                        let option = document.createElement("option");
                        option.value = opt;
                        option.textContent = opt;
                        selectField.appendChild(option);
                    });
                }
            }
        }
    }

    populateAcademicYearOptions("academic_year_input", "academic_year_select");

});


