const express = require('express')
const multer = require('multer')
const path = require('path')
const app = express()
const fs = require('fs')
const PORT = 8080
app.use('/uploads', express.static(path.join(__dirname, 'uploads')))
app.use('/public', express.static(path.join(__dirname, 'public')))
app.use(express.json({ limit: '100mb' }))
app.use(express.urlencoded({ extended: true, limit: '100mb' }))

let tracks;

// Чистка tracks.json від треків, яких немає в uploads
async function cleanStorage() {
    if (!Array.isArray(tracks) || tracks.length === 0) return;
    let existingTracks = tracks.filter(track => {
        let filePath = path.join(__dirname, track.url.replace(/^\//, ''))
        return fs.existsSync(filePath)
    })
    tracks = existingTracks
    fs.writeFileSync('public/tracks.json', JSON.stringify(existingTracks, null, 1))
}

async function updateStorage(){ // Видалити треки, яких немає в tracks.json
    let uploadsRAW = fs.readdirSync("uploads")
    let uploads = uploadsRAW.filter(el => el.endsWith(".mp3"))
    uploads.forEach(filename => {
        let trackExists = tracks.find(track => filename.endsWith(track.name) || track.fileName == filename)
        if(!trackExists){
            fs.unlink(path.join(__dirname, 'uploads/', filename), (err) => {
                if (err) { return console.error(`Error, something went wrong`) }
                else console.log("🧹 Видалено невикористаний файл:", filename)
            })
        }
    })
}
async function cleanImages() {
    let allUploads = fs.readdirSync("uploads")
    let images = allUploads.filter(file => /\.(jpg|jpeg|png|webp)$/i.test(file))
    let usedImages = tracks.map(track => track.imgUrl?.split('/').pop()).filter(Boolean)
    images.forEach(image => {
        let count = usedImages.filter(img => img === image).length
        if (count === 0) {
            fs.unlink(path.join(__dirname, 'uploads', image), (err) => {
                if (err) console.error("Не вдалося видалити:", image, err.message)
                else console.log("🧹 Видалено невикористане зображення:", image)
            })
        }
    })
}
async function updateTracks(){ // ініціалізація файлу tracks.json
    if(fs.existsSync('public/tracks.json')){
        tracks = JSON.parse(fs.readFileSync('public/tracks.json', "utf8"))
        await cleanStorage()
        await updateStorage()
        await cleanImages()
    }else{ tracks = []; return console.error(`Error reading tracks.json`) }
}

// Validating storage
const storage = multer.diskStorage({
    destination: (req, file, cb) => cb(null, 'uploads/'),
    filename: (req, file, cb) => cb(null, Date.now() + '-' + file.originalname.replace(/[^\w\d\-_\.]/g, '_'))
})
const upload = multer({ 
    storage,
    limits: { fileSize: 100 * 1024 * 1024 } // 100 MB
})

// Pages
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'))
})
app.get('/albums.html', (req, res) => {
    res.sendFile(path.join(__dirname, 'albums.html'))
})
app.get('/singles.html', (req, res) => {
    res.sendFile(path.join(__dirname, 'singles.html'))
})
app.get('/load:pass', (req, res) => {
    if(req.params.pass == "12072012"){
        res.sendFile(path.join(__dirname, 'load.html'))
    }
})

// POST процеси
app.post('/upload', upload.fields([{ name: "file" }, { name: "image" }]), (req, res) => {
    try{
        let singleName = req.body.singleName
        let file = req.files["file"][0]
        let image = req.files["image"][0]
        if(!singleName || !file || !image){
            return res.status(404).send(`Error`)
        }
        tracks.push({
            single_name: singleName,
            name: file.originalname,
            fileName: file.filename,
            url: `/uploads/${file.filename}`,
            imgUrl: `/uploads/${image.filename}`
        })
        fs.writeFileSync('public/tracks.json', JSON.stringify(tracks, null, 1))
        res.send(`Success`)
    }catch(error){
        return res.status(404).send(`Error`)
    }
    
})
app.post('/uploadAlbum', upload.fields([{ name: "files" }, { name: "albumImage" }]), (req, res) => {
    try{
        let albumName = req.body.albumName
        let files = req.files["files"]
        let image = req.files["albumImage"][0]
        if(!albumName || !files || !image){
            return res.status(404).send(`Error`)
        }
        for(let i=0;i<files.length;i++){
            let file = files[i]
            tracks.push({
                name: file.originalname,
                url: `/uploads/${file.filename}`,
                album: albumName,
                fileName: file.filename,
                imgUrl: `/uploads/${image.filename}`
            })
        }
        fs.writeFileSync('public/tracks.json', JSON.stringify(tracks, null, 1))
        res.send(`Success`)
    }catch(error){
        return res.status(404).send(`Error some: ${error}`)
    }
})

updateTracks()

app.listen(PORT, () => {
    console.log(`Сервер працює на http://localhost:${PORT}`)
})