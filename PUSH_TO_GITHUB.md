# Step-by-Step: Push Project to GitHub

Aap ye steps ek-ek karke follow karein. Har step ke baad next step pe jayein.

---

## Step 1: Terminal / PowerShell kholo

- **Cursor** mein: **Terminal → New Terminal** (ya `Ctrl + `` `)
- Ya Windows **PowerShell** / **Command Prompt** kholo

---

## Step 2: Project folder mein jao

Ye command type karo aur **Enter** dabao:

```
cd "C:\Users\shike\OneDrive\Desktop\stock-prediction-modell-main"
```

---

## Step 3: GitHub repo ka URL decide karo

- Apna **existing GitHub repo** browser mein kholo
- **Code** button pe click karo
- **HTTPS** wala URL copy karo  
  Example: `https://github.com/yourusername/your-repo-name.git`

*(Agar aap SSH use karte ho to `git@github.com:yourusername/your-repo-name.git` wala copy karo.)*

---

## Step 4: Remote add karo

Neeche wali line mein **apna actual URL** paste karo (jo aapne copy kiya), phir **Enter**:

```
git remote add origin PASTE_YOUR_URL_HERE
```

**Example** (sirf example, apna URL use karein):  
`git remote add origin https://github.com/yourusername/stock-prediction.git`

Agar koi error aaye "remote origin already exists", to pehle ye chalao:  
`git remote remove origin`  
phir dubara **Step 4** wali command chalao.

---

## Step 5: Branch name fix karo (agar GitHub pe "main" use hota hai)

GitHub pe aajkal default branch **main** hoti hai. Humari local branch **master** hai. Dono ko match karne ke liye ye chalao:

```
git branch -M main
```

*(Agar aapko pata hai repo pe "master" hi use hoti hai, to ye step skip kar sakte ho.)*

---

## Step 6A: Agar aap **purana GitHub code replace** karna chahte ho (sirf yehi code rahe)

Matlab: GitHub pe jo bhi hai use hata ke isi folder ka code upload karna hai.

Ye do commands chalao, ek ke baad ek:

```
git push -u origin main --force
```

Pehli baar push pe GitHub **login** ya **token** maang sakta hai — wahi use karo.

---

## Step 6B: Agar aap **purana GitHub code bhi rakhna** chahte ho (merge karke push)

Matlab: GitHub pe jo commits pehle se hain + ye naya code dono rahene chahiye.

Pehle ye:

```
git pull origin main --allow-unrelated-histories --no-edit
```

Agar **conflict** aaye to terminal batayega kis file mein — woh file khol ke conflict resolve karo, phir:

```
git add .
git commit -m "Merge remote with local"
git push -u origin main
```

Agar koi conflict nahi aaya, to seedha:

```
git push -u origin main
```

---

## Step 7: Check karo

- Browser mein apna **GitHub repo** kholo
- Dekho: `backend-drf`, `frontend-react`, `nginx`, `docker-compose.yml` wagaira sab dikh rahe hain

Agar sab dikh raha hai to **ho gaya** — code GitHub pe push ho chuka hai.

---

## Short summary (order of steps)

| Step | Kya karna hai |
|------|----------------|
| 1 | Terminal kholo |
| 2 | `cd "C:\Users\shike\OneDrive\Desktop\stock-prediction-modell-main"` |
| 3 | GitHub repo ka URL copy karo |
| 4 | `git remote add origin <your-url>` |
| 5 | `git branch -M main` |
| 6 | **6A** ya **6B** mein se ek choose karke push wali command chalao |
| 7 | GitHub pe open karke verify karo |

Kisi step pe error aaye to error ka exact message copy karke bhej dena, hum usi ke hisaab se next step bata denge.
