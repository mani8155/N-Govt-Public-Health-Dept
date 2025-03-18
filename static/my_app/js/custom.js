// $(document).ready(function () {
//     // Global file validation function
//     function validateFileSize(input) {
//         const file = input.files[0];
//
//         if (file) {
//             const size = (file.size / 1024 / 1024).toFixed(2);
//             const output = $(input).closest('.col').find('p'); // Find the corresponding output <p>
//
//             if (size > 2) {
//                 output.html('<b class="text-danger">File size must be less than or equal to 2MB</b>');
//                 $(input).val(''); // Clear file input
//                 $(input).addClass('is-invalid'); // Bootstrap error styling
//             } else {
//                 output.html('<b class="text-success">File size is: ' + size + " MB</b>");
//                 $(input).removeClass('is-invalid'); // Remove error styling if valid
//             }
//         }
//     }
//
//     // Attach event listener to all file inputs
//     $("input[type='file']").on('change', function () {
//         validateFileSize(this);
//     });
// });

$(document).ready(function () {
    // Global file validation function
    function validateFileSize(input) {
        const file = input.files[0];

        if (file) {
            const size = (file.size / 1024 / 1024).toFixed(2);
            const output = $(input).closest('.col').find('p'); // Find the corresponding output <p>

            if (size > 2) {
                output.html('<b class="text-danger">File size must be less than or equal to 2MB</b>');
                $(input).val(''); // Clear file input
                $(input).addClass('is-invalid'); // Bootstrap error styling
            } else {
                output.html('');
                $(input).removeClass('is-invalid'); // Remove error styling if valid
            }
        }
    }

    // Attach event listener to all file inputs
    $("input[type='file']").on('change', function () {
        validateFileSize(this);
    });
});
