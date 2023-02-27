const prevBtns= document.getElementById("prev")
const nextBtns= document.querySelectorAll(".btn-next")
const progress = document.getElementById('progress')


const formsteps=document.querySelectorAll(".form-step")

const progressSteps =document.querySelectorAll(".progress-step");

let formstepsnum= 0;

nextBtns.forEach(btn =>{
    btn.addEventListener("click", ()=>{
        formstepsnum ++;
        updateformsteps();
        updateprogressbar();
    })
})

prevBtns.addEventListener("click", ()=>{
        formstepsnum --;
        updateformsteps();
        updateprogressbar();
    })



function updateformsteps(){
    formsteps.forEach(step =>[
        step.classList.contains("form-step-active") && 
        step.classList.remove("form-step-active")
    ])
    formsteps[formstepsnum].classList.add("form-step-active")
}

function updateprogressbar(){
    progressSteps.forEach((progressStep, idx) => {
        if(idx < formstepsnum + 1){
            progressStep.classList.add("progress-step-active")
        }
        else{
            progressStep.classList.remove("progress-step-active")
        }
        
    
   
    })
    const progressActive= document.querySelectorAll(".progress-step-active")

        progress.style.width = ((progressActive.length - 1 ) / (progressSteps.length - 1)) * 100 + "%";

}  