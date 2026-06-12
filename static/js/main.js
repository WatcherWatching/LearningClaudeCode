document.addEventListener('DOMContentLoaded', () => {
    const howItWorksBtn = document.getElementById('how-it-works-btn');
    const modal = document.getElementById('video-modal');
    const closeModalBtn = document.getElementById('close-modal');
    const modalVideo = document.getElementById('modal-video');

    const videoUrl = 'https://www.youtube.com/embed/dQw4w9WgXcQ'; // Placeholder URL

    if (howItWorksBtn && modal) {
        howItWorksBtn.addEventListener('click', (e) => {
            e.preventDefault();
            modalVideo.src = videoUrl;
            modal.style.display = 'flex';
        });

        const closeModal = () => {
            modal.style.display = 'none';
            modalVideo.src = ''; // Stop video by clearing src
        };

        closeModalBtn.addEventListener('click', closeModal);

        window.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeModal();
            }
        });
    }
});
