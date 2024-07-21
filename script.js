class VisualNovel {
    constructor(scenes) {
        this.scenes = scenes;
        this.currentSceneIndex = 0;
        this.currentElementIndex = 0;
        this.characterImages = {};
        this.backgroundDiv = document.getElementById('background');
        this.charactersDiv = document.getElementById('characters');
        this.characterNameDiv = document.getElementById('character-name');
        this.dialogueDiv = document.getElementById('dialogue');
        this.prevBtn = document.getElementById('prev-btn');
        this.nextBtn = document.getElementById('next-btn');
        this.audio = new Audio();
        this.currentAudioSrc = '';
  
        this.preloadImages();
        this.bindEvents();
        this.displayScene();
    }

    preloadImages() {
        this.scenes.forEach(scene => {
            new Image().src = scene.background_image;
            scene.characters.forEach(character => {
                if (!this.characterImages[character]) {
                    let charImg = new Image();
                    charImg.src = `./images/${character}.png`;
                    this.characterImages[character] = charImg;
                }
            });
        });
    }

    bindEvents() {
        this.nextBtn.addEventListener('click', () => this.nextElement());
        this.prevBtn.addEventListener('click', () => this.prevElement());
        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowRight') this.nextElement();
            if (e.key === 'ArrowLeft') this.prevElement();
        });
    }

    displayScene() {
        let currentScene = this.scenes[this.currentSceneIndex];
        let currentElement = currentScene.story_elements[this.currentElementIndex];

        this.backgroundDiv.style.backgroundImage = `url(${currentScene.background_image})`;
        this.charactersDiv.innerHTML = '';

        if (currentElement.element_type === "dialogue") {
            let character = currentElement.content.character_name;
            let charImg = this.characterImages[character];
            if (charImg) {
                this.charactersDiv.appendChild(charImg.cloneNode());
            }
            this.characterNameDiv.textContent = character;
            this.dialogueDiv.textContent = currentElement.content.dialogue_text;
        } else if (currentElement.element_type === "narration") {
            this.characterNameDiv.textContent = '';
            this.dialogueDiv.textContent = currentElement.content.narration_text;
        }

        if (currentScene.music && (currentScene.music !== this.currentAudioSrc)) {
            this.audio.src = currentScene.music;
            this.currentAudioSrc = currentScene.music;
            this.audio.addEventListener('ended', () => {
                this.audio.play();
            });
            this.audio.play();
        }

        this.updateControls();
    }

    nextElement() {
        if (this.currentElementIndex < this.scenes[this.currentSceneIndex].story_elements.length - 1) {
            this.currentElementIndex++;
        } else if (this.currentSceneIndex < this.scenes.length - 1) {
            this.currentSceneIndex++;
            this.currentElementIndex = 0;
        }
        this.displayScene();
    }

    prevElement() {
        if (this.currentElementIndex > 0) {
            this.currentElementIndex--;
        } else if (this.currentSceneIndex > 0) {
            this.currentSceneIndex--;
            this.currentElementIndex = this.scenes[this.currentSceneIndex].story_elements.length - 1;
        }
        this.displayScene();
    }

    updateControls() {
        this.prevBtn.disabled = this.currentSceneIndex === 0 && this.currentElementIndex === 0;
        this.nextBtn.disabled = this.currentSceneIndex === this.scenes.length - 1 &&
                                this.currentElementIndex === this.scenes[this.currentSceneIndex].story_elements.length - 1;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    fetch('story.json')
        .then(response => response.json())
        .then(data => new VisualNovel(data.scenes))
        .catch(error => console.error('Error loading story:', error));
});
