function get_data() {
    var j_title = document.getElementById("job_title").value
    var exp = document.getElementById("exp").value
    var tech_skill = document.getElementById("tech_skill").value
    var qualification = document.getElementById("qualification").value
    var responsibilities = document.getElementById("responsibilities").value
    var domain_exp = document.getElementById("domain_exp").value

    var result = "Job Title: " + j_title + "\nExperience: " + exp + "\nTechnical Skills: " + tech_skill + "\nQualification: " + qualification + "\nResponsibilities: " + responsibilities + "\nDomain Experience: " + domain_exp
    return result
}

function get_loader() {
    const loader = document.createElement("div")
    loader.classList.add("card")
    loader.classList.add("blur")

    const center_body = document.createElement("div")
    center_body.classList.add("center-body")
    const loader_circle = document.createElement("div")
    loader_circle.classList.add("loader-circle-2")

    center_body.append(loader_circle)
    loader.append(center_body)
    return loader
}

function handle_click(event) {
    event.preventDefault();
    const op_1 = document.getElementById("op_1")
    const op_2 = document.getElementById("op_2")
    let query = JSON.stringify({
        query: get_data()
    })

    op_1.innerHTML = ""
    op_2.innerHTML = ""

    op_1.append(get_loader())
    op_2.append(get_loader())

    const response = fetch("http://127.0.0.1:8000/get_jd", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: query,
    })
        .then((resp) => resp.json())
        .then((result) => {
            op_1.innerHTML = ""
            console.log(result)
            op_1.innerHTML = marked.parse(JSON.parse(result[0]).result)
            
            const response_2 = fetch("http://127.0.0.1:8000/get_question", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: query,
            })
                .then((resp) => resp.json())
                .then((result2) => {
                    op_2.innerHTML = ""
                    console.log(result2)
                    op_2.innerHTML = marked.parse(JSON.parse(result2[0]).result)
                })
        })



}

document.getElementById("jd_create").addEventListener("click", handle_click)

// function handle_click_2(event) {
//     event.preventDefault();
//     const op_1 = document.getElementById("op_1")
//     const op_2 = document.getElementById("op_2")
//     let query = JSON.stringify({
//         query: get_data()
//     })


//     op_1.innerHTML = ""
//     op_2.innerHTML = ""

//     const loader = document.createElement("div")
//     loader.classList.add("left_card")
//     loader.classList.add("blur")

//     const center_body = document.createElement("div")
//     center_body.classList.add("center-body")
//     const loader_circle = document.createElement("div")
//     loader_circle.classList.add("loader-circle-2")

//     center_body.append(loader_circle)
//     loader.append(center_body)
//     op_1.append(loader)
//     op_2.append(loader)



//     const response = fetch("http://127.0.0.1:8000/get_question", {
//         method: "POST",
//         headers: {
//             "Content-Type": "application/json",
//         },
//         body: query,
//     })
//         .then((resp) => resp.json())
//         .then((result) => {
//             console.log(result)
//             op_2.innerHTML = marked.parse(JSON.parse(result[0]).result)
//         })

// }

// document.getElementById("ques_create").addEventListener("click", handle_click_2)