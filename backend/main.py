from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from products.router import router as products_router
from contact.router import router as contact_router
from users.router import router as users_router

app = FastAPI(title="Halfsy API")

app.include_router(products_router)
app.include_router(contact_router)
app.include_router(users_router)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def root():
    return {"message": "Halfsy API Running"}
