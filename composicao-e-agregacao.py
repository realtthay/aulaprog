from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# configurações
app = Flask(__name__)
path = os.path.dirname(os.path.abspath(__file__))
arquivobd = os.path.join(path, 'profissoes.db')
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///"+arquivobd
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # remover warnings
db = SQLAlchemy(app)


class Casa (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    formato = db.Column(db.String(254))
    
    # lista reversa!
    quartos = db.relationship("Quarto", backref="casa")

    def __str__(self):
        return f'Casa: {self.formato}'        
        
class Quarto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(254))
    dimensoes = db.Column(db.String(254))

    casa_id = db.Column(db.Integer, db.ForeignKey(Casa.id), 
                          nullable=False)
    # não precisa do comando relationship, pois a lista reversa
    # em Casa já cria o atributo "casa" em Quarto
    #casa = db.relationship("Casa")

    # lista reversa de mobilias no quarto
    # além da lista "mobilias" nesta classe, 
    # será criado atributo "quarto" em Mobilia
    mobilias = db.relationship("Mobilia", backref="quarto")

    def __str__(self):
        s = f'Quarto: {self.nome}, {self.dimensoes}, em: {str(self.casa)}'
        s += f'na casa: {str(self.casa)}'          
        return s

class Mobilia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(254))
    funcao = db.Column(db.String(254))
    material = db.Column(db.String(254))
    
    type = db.Column(db.String(50))

    __maper__args__ = {
        'polymorphic_identity':'mobilia',
        'polymorphic_on':type
         }
        
    quarto_id = db.Column(db.Integer, db.ForeignKey(Quarto.id), 
                nullable=True) # a mobilia pode estar em um quarto, ou não
        
 
    def __str__(self): # expressão do objeto em forma textual
        s = f'Mobília: ({self.id}) {self.nome}, '+\
               f'{self.funcao}, {self.material}'
        if self.quarto:
            s += f', localizada em: {str(self.quarto)}'
        return s

class Televisao(Mobilia):
    id = db.Column(db.Integer, db.ForeignKey('mobilia.id'), primary_key=True)
    __mapper_args__ = {
        'polymorphic_identity': 'televisao',
    }
    polegadas = db.Column(db.Float)
    def __str__(self):
     return super().__str__() + f", polegadas={self.polegadas}"

class Computador(Mobilia):
    id = db.Column(db.Integer, db.ForeignKey ('mobilia.id'), primary_key=True)
    __mapper_args__ = {
        'polymorphic_identity':'computador'
    }
    memoria = db.Column(db.Float(50))
    def __str__(self):
        return f'{super().__str__()}, memoria: {self.memoria}'



if __name__ == "__main__": # teste das classes
    
    if os.path.exists(arquivobd): # se houver o arquivo...
        os.remove(arquivobd) # ...apagar!

    db.create_all() # criar tabelas

    print("*** TESTE criando objetos")

    c1 = Casa(formato="Germânica") # cria uma casa

    # persiste para criar o id
    db.session.add(c1)
    db.session.commit()

    print(c1) # exibir atributos da casa

    q1 = Quarto(nome="Sala", dimensoes="6x5 metros", casa=c1)
    q2 = Quarto(nome="Banheiro", dimensoes="3x4 metros", casa=c1)
    
    db.session.add(q1)
    db.session.add(q2)
    db.session.commit()

    print(q1, q2)

    print("*** TESTE com todos os dados")
    print(c1) # casa
    # quartos da casa, sem lista reversa
    for q in db.session.query(Quarto).filter(Quarto.casa_id == c1.id).all():
        print(q)

    print("*** TESTE com todos os dados, via lista reversa")
    print(c1) # casa
    # quartos da casa, com lista reversa
    for q in c1.quartos:
        print(q)

    print("*** TESTE das mobílias")
    m1 = Mobilia(nome = "Armário", funcao = "Guardar coisas", 
        material = "Madeira", quarto=q1) 
    db.session.add(m1)
    db.session.commit()
    print(m1)

    m2 = Mobilia(nome = "Espelho", funcao = "Ajudar a se arrumar", 
        material = "Vidro polido")  # não está em nenhum quarto
    db.session.add(m2)
    db.session.commit()
    print(m2)

    t1 = Televisao(nome = "Samsung", funcao = "Assistir canais", material = "plastico", polegadas = "50", quarto=q1)
    db.session.add(t1)
    db.session.commit()
    print(t1)

    cp1 = Computador( nome = "Philco", funcao = "Navegar na internet", material = "plastico", memoria = "530", quarto=q1)
    db.session.add(c1)
    db.session.commit()
    print(cp1)


    print("*** TESTE exibindo novamente todos os dados")
    print("*** TESTE com todos os dados CONECTADOS, via lista reversa")
    print("*** não vai exibir mobílias que não estão em quartos")
    print(c1) # casa
    # quartos da casa, com lista reversa
    for q in c1.quartos:
        print(q)
        for m in q.mobilias:
            print(m)