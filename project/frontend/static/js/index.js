
$(function () {
    $("#btnSearch").click(function () {
        let query = $("#querySearch").val();
        if (query.length !== 0) {
            let csrf = $('input[name=csrfmiddlewaretoken]').val();
            $.ajax({
                url: ".",
                method: "POST",
                dataType: 'json',
                data: {
                    "query": query,
                    "use": "search_in_database",
                    csrfmiddlewaretoken: csrf,
                },

                success: function (response, status) {
                    content = JSON.parse(response['content']);
                    renderHtmlAnswers(content);
                    runDropDown();
                }
            });
        }
    })

    function renderHtmlAnswers(content) {
        let answer = "";
        for (key in content) {
            answer += `
                <div class="group">
                    <button class="dropdown-btn">
                        ${key}.txt
                        <i class="fa fa-caret-down"></i>
                    </button>
                    <div class="dropdown-container">
                        <label>${content[key]}</label>
                    </div>
                </div>
                <br />
            `
        }
        $("#app").html(answer);
    }

    function runDropDown() {
        let dropdown = $(".dropdown-btn");

        for (let i = 0; i < dropdown.length; i++) {
            dropdown[i].addEventListener("click", function () {
                this.classList.toggle("active");
                var dropdownContent = this.nextElementSibling;
                if (dropdownContent.style.display === "block") {
                    dropdownContent.style.display = "none";
                } else {
                    dropdownContent.style.display = "block";
                }
            });
        }
        if (dropdown.length !== 0) {
            dropdown[0].classList.toggle("active");
            dropdown[0].nextElementSibling.style.display = "block";
        }
    }

    function reTrain() {
        console.log("start");
        let csrf = $('input[name=csrfmiddlewaretoken]').val();
        $.ajax({
            url: ".",
            method: "POST",
            dataType: 'json',
            data: {
                "query": "",
                "use": "reTrain",
                csrfmiddlewaretoken: csrf,
            },

            success: function (response, status) {
                $('#inputfile').val("");
                console.log("ok");
            }
        });
    }

    let files = [];
    $("#send").click(function () {
        if (files.length !== 0) {
            for (index = 0; index < files.length; index++) {
                if (files[index].length !== 0) {
                    let data = { 'text': files[index] };
                    fetch('http://127.0.0.1:8090/data/api/data/', {
                        method: 'POST', // or 'PUT'
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(data),
                    })
                        .then(response => response.json())
                        .then(data => {
                        })
                        .catch((error) => {
                        });
                }
            }

            asyncFunction(reTrain, Math.max(200, 100 * files.length));
        }
    });

    $("#get").click(function () {
        const data = {};

        fetch('http://127.0.0.1:8090/data/api/data/', {
            method: 'GET', // or 'PUT'
        })
            .then(response => response.json())
            .then(data => {
                console.log('Success:', data);
            })
            .catch((error) => {
                console.error('Error:', error);
            });
    });

    function asyncFunction(callback, ms) {
        setTimeout(() => {
            callback();
        }, ms);
    }

    $("#inputfile").change(function () {
        let allFiles = this.files; //FileList object
        data = [];
        for (let index in allFiles)
            if (parseInt(index) < allFiles.length) {
                var fr = new FileReader();
                fr.onload = function () {
                    data.push(this.result);
                }
                fr.readAsText(this.files[index]);
            }
        asyncFunction(function () {
            files = data;
        }, 200);
    })
});
