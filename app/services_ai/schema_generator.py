# generate_schema_prompt.py
import re

def generate_db_schema(models_path="app/models.py") -> str:
# def parse_models_to_schema(models_path="app/models.py"):
    """
    models.py 파일을 분석하여 LLM용 SYSTEM_PROMPT 스키마 정의 텍스트를 생성합니다.
    """
    try:
        with open(models_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        return f"❌ 오류: '{models_path}' 파일을 찾을 수 없습니다. 경로를 확인해 주세요."

    schema_info = {}
    current_table = None

    # 정규식 패턴 정의
    class_pattern = re.compile(r"class\s+(\w+)\(")
    tablename_pattern = re.compile(r"__tablename__\s*=\s*['\"](\w+)['\"]")
    column_pattern = re.compile(r"(\w+)\s*=\s*Column\((.*)\)")
    relationship_pattern = re.compile(r"(\w+)\s*=\s*relationship\((.*)\)")

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        # 1. 클래스 진입 (기본 테이블명은 클래스명으로 임시 설정)
        class_match = class_pattern.search(line)
        if class_match:
            current_table = class_match.group(1)
            schema_info[current_table] = {
                "tablename": current_table,
                "columns": [],
                "relationships": []
            }
            continue

        if not current_table:
            continue

        # 2. 실제 __tablename__ 추출
        tablename_match = tablename_pattern.search(line)
        if tablename_match:
            schema_info[current_table]["tablename"] = tablename_match.group(1)
            continue

        # 3. Column 정보 추출 (PK, FK 포함)
        column_match = column_pattern.search(line)
        if column_match:
            col_name = column_match.group(1)
            col_details = column_match.group(2)

            # 타입 추출 (String, Integer, ForeignKey 등)
            col_type = "Unknown"
            if "Integer" in col_details: col_type = "INTEGER"
            elif "String" in col_details: col_type = "VARCHAR"
            elif "DateTime" in col_details: col_type = "DATETIME"
            elif "Boolean" in col_details: col_type = "BOOLEAN"
            elif "Text" in col_details: col_type = "TEXT"
            elif "Float" in col_details: col_type = "FLOAT"

            # 제약 조건 판단
            constraints = []
            if "primary_key=True" in col_details.replace(" ", ""):
                constraints.append("PRIMARY KEY")
            
            # ForeignKey 추출
            fk_match = re.search(r"ForeignKey\(['\"]([\w\.]+)['\"]", col_details)
            if fk_match:
                constraints.append(f"FOREIGN KEY REFERENCES {fk_match.group(1)}")

            constraint_str = f" ({', '.join(constraints)})" if constraints else ""
            schema_info[current_table]["columns"].append(f"  - {col_name}: {col_type}{constraint_str}")
            continue

        # 4. Relationship 및 back_populates 추출
        rel_match = relationship_pattern.search(line)
        if rel_match:
            rel_name = rel_match.group(1)
            rel_details = rel_match.group(2)
            
            # 연결된 대상 클래스 추출
            target_match = re.search(r"['\"](\w+)['\"]", rel_details)
            target_class = target_match.group(1) if target_match else "Unknown"
            
            # back_populates 추출
            bp_match = re.search(r"back_populates=['\"](\w+)['\"]", rel_details.replace(" ", ""))
            bp_str = f", back_populates='{bp_match.group(1)}'" if bp_match else ""

            schema_info[current_table]["relationships"].append(
                f"  - {rel_name} <-> {target_class}{bp_str}"
            )

    # 5. LLM을 위한 프롬프트 텍스트 형태로 변환
    prompt_output = "### DATABASE SCHEMA DEFINITION ###\n\n"
    for table_attr in schema_info.values():
        prompt_output += f"Table: {table_attr['tablename']}\n"
        prompt_output += "Columns:\n"
        for col in table_attr["columns"]:
            prompt_output += f"{col}\n"
        if table_attr["relationships"]:
            prompt_output += "Relationships:\n"
            for rel in table_attr["relationships"]:
                prompt_output += f"{rel}\n"
        prompt_output += "\n"
        
    return prompt_output

# Cache it once at startup
DB_SCHEMA = generate_db_schema()

if __name__ == "__main__":
    # 실제 프로젝트의 models.py 경로를 적어주세요.
    # 예: app/models.py 또는 app/database/models.py 등
    models_file_path = "app/models.py" 
    
    # db_schema_prompt = parse_models_to_schema(models_file_path)
    db_schema_prompt = generate_db_schema(models_file_path)
    
    print("✨ 파싱 완료! LLM SYSTEM_PROMPT에 주입할 스키마 텍스트 결과입니다:\n")
    print(db_schema_prompt)
    
    # # 선택 사항: 잘 추출되었는지 파일로도 저장해서 확인 가능합니다.
    # with open("extracted_schema.txt", "w", encoding="utf-8") as f:
    #     f.write(db_schema_prompt)
