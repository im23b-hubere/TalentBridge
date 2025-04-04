from flask import Blueprint, request, jsonify, current_app, send_from_directory
import os
from werkzeug.utils import secure_filename
from services.cv_service import CVService
from db.db_service import get_db_connection

cv_bp = Blueprint('cv', __name__, url_prefix='/api/cv')

# Standard-Endpoint für alle CVs, funktioniert mit beiden URLs:
# - /api/cv
# - /api/cv/cvs
@cv_bp.route('', methods=['GET'])
@cv_bp.route('/cvs', methods=['GET'])
def get_all_cvs():
    """Alle Lebensläufe abrufen"""
    tenant_id = request.args.get('tenant_id')
    
    # Datenbankverbindung herstellen
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Datenbankverbindung konnte nicht hergestellt werden"}), 500
    
    try:
        cv_service = CVService(conn)
        cvs = cv_service.get_all_cvs(tenant_id)
        
        return jsonify(cvs)
    except Exception as e:
        return jsonify({"error": f"Fehler beim Abrufen der Lebensläufe: {str(e)}"}), 500
    finally:
        conn.close()

@cv_bp.route('/<cv_id>', methods=['GET'])
def get_cv_by_id(cv_id):
    """Einen spezifischen Lebenslauf abrufen"""
    tenant_id = request.args.get('tenant_id')
    
    # Datenbankverbindung herstellen
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Datenbankverbindung konnte nicht hergestellt werden"}), 500
    
    try:
        cv_service = CVService(conn)
        cv = cv_service.get_cv_by_id(cv_id, tenant_id)
        
        if not cv:
            return jsonify({"error": "Lebenslauf nicht gefunden"}), 404
        
        return jsonify(cv)
    except Exception as e:
        return jsonify({"error": f"Fehler beim Abrufen des Lebenslaufs: {str(e)}"}), 500
    finally:
        conn.close()

@cv_bp.route('/employee/<employee_id>', methods=['POST'])
def create_cv(employee_id):
    """Einen neuen Lebenslauf erstellen"""
    tenant_id = request.args.get('tenant_id')
    data = request.json
    
    # Datenbankverbindung herstellen
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Datenbankverbindung konnte nicht hergestellt werden"}), 500
    
    try:
        cv_service = CVService(conn)
        cv = cv_service.create_cv(employee_id, data, tenant_id)
        
        if not cv:
            return jsonify({"error": "Lebenslauf konnte nicht erstellt werden"}), 400
        
        return jsonify(cv), 201
    except Exception as e:
        return jsonify({"error": f"Fehler beim Erstellen des Lebenslaufs: {str(e)}"}), 500
    finally:
        conn.close()

@cv_bp.route('/<cv_id>', methods=['PUT'])
def update_cv(cv_id):
    """Einen Lebenslauf aktualisieren"""
    tenant_id = request.args.get('tenant_id')
    data = request.json
    
    # Datenbankverbindung herstellen
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Datenbankverbindung konnte nicht hergestellt werden"}), 500
    
    try:
        cv_service = CVService(conn)
        cv = cv_service.update_cv(cv_id, data, tenant_id)
        
        if not cv:
            return jsonify({"error": "Lebenslauf nicht gefunden"}), 404
        
        return jsonify(cv)
    except Exception as e:
        return jsonify({"error": f"Fehler beim Aktualisieren des Lebenslaufs: {str(e)}"}), 500
    finally:
        conn.close()

@cv_bp.route('/<cv_id>', methods=['DELETE'])
def delete_cv(cv_id):
    """Einen Lebenslauf löschen"""
    tenant_id = request.args.get('tenant_id')
    
    # Datenbankverbindung herstellen
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Datenbankverbindung konnte nicht hergestellt werden"}), 500
    
    try:
        cv_service = CVService(conn)
        result = cv_service.delete_cv(cv_id, tenant_id)
        
        if not result:
            return jsonify({"error": "Lebenslauf nicht gefunden"}), 404
        
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": f"Fehler beim Löschen des Lebenslaufs: {str(e)}"}), 500
    finally:
        conn.close()

@cv_bp.route('/employee/<employee_id>/photo', methods=['POST'])
def upload_photo(employee_id):
    """Ein Foto für einen Mitarbeiter hochladen"""
    tenant_id = request.args.get('tenant_id')
    
    if 'photo' not in request.files:
        return jsonify({"error": "Keine Datei angegeben"}), 400
    
    file = request.files['photo']
    
    if file.filename == '':
        return jsonify({"error": "Keine Datei ausgewählt"}), 400
    
    # Datenbankverbindung herstellen
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Datenbankverbindung konnte nicht hergestellt werden"}), 500
    
    try:
        cv_service = CVService(conn)
        photo_url = cv_service.upload_photo(employee_id, file, tenant_id)
        
        if not photo_url:
            return jsonify({"error": "Foto konnte nicht hochgeladen werden"}), 400
        
        return jsonify({"photoUrl": photo_url})
    except Exception as e:
        return jsonify({"error": f"Fehler beim Hochladen des Fotos: {str(e)}"}), 500
    finally:
        conn.close()

@cv_bp.route('/<cv_id>/export/<template_id>', methods=['GET'])
def export_cv(cv_id, template_id):
    """Einen Lebenslauf mit einer Vorlage exportieren"""
    tenant_id = request.args.get('tenant_id')
    
    # Datenbankverbindung herstellen
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Datenbankverbindung konnte nicht hergestellt werden"}), 500
    
    try:
        cv_service = CVService(conn)
        result = cv_service.export_cv_with_template(cv_id, template_id, tenant_id)
        
        if not result:
            return jsonify({"error": "Export konnte nicht durchgeführt werden"}), 400
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Fehler beim Exportieren des Lebenslaufs: {str(e)}"}), 500
    finally:
        conn.close()

# Routen für Skill-Kategorien
@cv_bp.route('/skill-categories', methods=['GET'])
def get_skill_categories():
    """Alle Skill-Kategorien abrufen"""
    # Datenbankverbindung herstellen
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Datenbankverbindung konnte nicht hergestellt werden"}), 500
    
    try:
        cursor = conn.cursor()
        categories = cursor.execute(
            "SELECT id, name FROM skill_categories ORDER BY name"
        ).fetchall()
        
        result = [{"id": cat[0], "name": cat[1]} for cat in categories]
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Fehler beim Abrufen der Skill-Kategorien: {str(e)}"}), 500
    finally:
        conn.close()

# Routen für Skills
@cv_bp.route('/skills', methods=['GET'])
def get_skills():
    """Alle Skills abrufen, optional nach Kategorie gefiltert"""
    category_id = request.args.get('category_id')
    
    # Datenbankverbindung herstellen
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Datenbankverbindung konnte nicht hergestellt werden"}), 500
    
    try:
        cursor = conn.cursor()
        
        query = """
            SELECT s.id, s.name, sc.id as category_id, sc.name as category
            FROM skills s
            JOIN skill_categories sc ON s.category_id = sc.id
        """
        
        params = []
        if category_id:
            query += " WHERE s.category_id = %s"
            params.append(category_id)
            
        query += " ORDER BY sc.name, s.name"
        
        skills = cursor.execute(query, params).fetchall()
        
        result = [
            {
                "id": skill[0], 
                "name": skill[1], 
                "categoryId": skill[2], 
                "category": skill[3]
            } 
            for skill in skills
        ]
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Fehler beim Abrufen der Skills: {str(e)}"}), 500
    finally:
        conn.close()

@cv_bp.route('/skills', methods=['POST'])
def create_skill():
    """Einen neuen Skill erstellen"""
    data = request.json
    
    if not data or 'name' not in data or 'categoryId' not in data:
        return jsonify({"error": "Name und Kategorie sind erforderlich"}), 400
    
    # Datenbankverbindung herstellen
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Datenbankverbindung konnte nicht hergestellt werden"}), 500
    
    try:
        cursor = conn.cursor()
        
        # Prüfen, ob die Kategorie existiert
        category = cursor.execute(
            "SELECT id FROM skill_categories WHERE id = %s",
            (data['categoryId'],)
        ).fetchone()
        
        if not category:
            return jsonify({"error": "Kategorie nicht gefunden"}), 404
        
        # Prüfen, ob der Skill bereits existiert
        existing_skill = cursor.execute(
            "SELECT id FROM skills WHERE name = %s AND category_id = %s",
            (data['name'], data['categoryId'])
        ).fetchone()
        
        if existing_skill:
            return jsonify({"error": "Skill existiert bereits in dieser Kategorie"}), 409
        
        # Skill erstellen
        skill_id = cursor.execute(
            "INSERT INTO skills (name, category_id) VALUES (%s, %s) RETURNING id",
            (data['name'], data['categoryId'])
        ).fetchone()[0]
        
        # Neuen Skill zurückgeben
        skill = cursor.execute(
            """
            SELECT s.id, s.name, sc.id as category_id, sc.name as category
            FROM skills s
            JOIN skill_categories sc ON s.category_id = sc.id
            WHERE s.id = %s
            """,
            (skill_id,)
        ).fetchone()
        
        return jsonify({
            "id": skill[0], 
            "name": skill[1], 
            "categoryId": skill[2], 
            "category": skill[3]
        }), 201
    except Exception as e:
        return jsonify({"error": f"Fehler beim Erstellen des Skills: {str(e)}"}), 500
    finally:
        conn.close() 