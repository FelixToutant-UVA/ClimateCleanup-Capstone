// script.js

document.addEventListener("DOMContentLoaded", () => {
    // Contact form handling
    const contactForm = document.getElementById("contact-form")
    if (contactForm) {
      contactForm.addEventListener("submit", (e) => {
        e.preventDefault()
  
        // Gather form data
        const formData = new FormData(contactForm)
        const data = {}
        formData.forEach((value, key) => {
          data[key] = value
        })
  
        console.log("Form Data Submitted:", data)
        alert("Thank you for your message! We'll get back to you soon.")
  
        // Reset the form fields
        contactForm.reset()
      })
    }
  
    // Initialize any other interactive elements
    const heroBtn = document.querySelector(".hero-btn")
    if (heroBtn) {
      heroBtn.addEventListener("click", () => {
        window.location.href = "/food-forests"
      })
    }
  })
  