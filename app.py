import os
from flask import Flask,render_template,request,redirect,url_for,flash
from graph import graph
from report_analyzer import(extract_text_from_pdf, analyze_medical_report, extract_report_values)
from scan_analyzer import analyze_medical_scan  
from flask_login import login_user, logout_user, login_required, current_user
from dotenv import load_dotenv
from extensions import db,login_manager
from models import User,Profile,ChatHistory,Report,ReportValue,Scan
from langchain_groq import ChatGroq
llm = ChatGroq(model="qwen/qwen3.6-27b",reasoning_effort="none",max_tokens=800)

load_dotenv()

app=Flask(__name__)

app.config["SECRET_KEY"]=os.getenv("SECRET_KEY")
database_url=os.getenv("DATABASE_URL")
if database_url:
    if database_url.startswith("postgres://"):
        database_url = database_url.replace(
            "postgres://",
            "postgresql://",
            1
        )
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mani.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User,int(user_id))


with app.app_context():
    db.create_all()



@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register",methods=["GET","POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    if request.method=="POST":
        name=request.form.get("name","").strip()
        email=request.form.get("email","").strip().lower()
        password=request.form.get("password","")
        confirm_password=request.form.get("confirm_password","")

        if not name or not email or not password:
            flash("Please fill in all required fields.", "error")
            return render_template("register.html")
        if len(password)<6:
            flash("Password must be atleast 6 characters", "error")
            return render_template("register.html")
        if password!=confirm_password:
            flash("Passwords don't match", "error")
            return render_template("register.html")
        existing_user=User.query.filter_by(email=email).first()
        if existing_user:
            flash("An account with this email already exists","error")
            return render_template("register.html")
        user=User(name=name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()
        profile=Profile(user_id=user.id)
        db.session.add(profile)
        db.session.commit()
        login_user(user)
        flash("Account created successfully","success")
        return redirect(url_for("home"))
    return render_template("register.html")

@app.route("/login",methods=["GET","POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    if request.method=="POST":
        email=request.form.get("email","").strip().lower()
        password=request.form.get("password","")
        user=User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("home"))
        flash("invalid email or password","error")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("you have been logged out","success")
    return redirect(url_for("home"))


    
@app.route("/research",methods=["GET","POST"])
@login_required
def research():
    analysis=None
    if request.method=="POST":
        query=request.form["query"]
        result=graph.invoke({"query":query})
        analysis=result["analysis"]

        history_item=ChatHistory(user_id=current_user.id, query=query, analysis=analysis)
        db.session.add(history_item)
        db.session.commit()

    return render_template(
        "research.html",
        analysis=analysis
    )

@app.route("/reports", methods=["GET","POST"])
@login_required
def reports():
    analysis=None
    error=None
    filename=None
    if request.method=="POST":
        file=request.files.get("report")
        if not file or file.filename=="":
            error="Please select a valid PDF report"
        elif not file.filename.lower().endswith(".pdf"):
            error="only PDF files are currently supported"
        else:
            filename=file.filename
            text=extract_text_from_pdf(file)
            if not text:
                error=("We cannot extract readable text")
            else:
                analysis=analyze_medical_report(text)
                if not analysis:
                    error=("Something went wrong")
                else:
                    report_values=extract_report_values(text)
                    print("\nExtracted Report Values: ")
                    print(report_values)
                    report = Report(user_id=current_user.id, report_name=filename,analysis=analysis)
                    db.session.add(report)
                    for item in report_values:
                        report_value=ReportValue(parameter=item["parameter"],value=item["value"],unit=item["unit"],reference_range=item["reference_range"])
                        report.values.append(report_value)
                    try:
                        db.session.commit()
                        print(f"Report saved with"f"{len(report_values)} values")
                    except Exception as e:
                        db.session.rollback()
                        print("Database error",e)
                        error=("Report was not saved")
    return render_template("reports.html",analysis=analysis, error=error, filename=filename)

@app.route("/scans", methods=["GET","POST"])
@login_required
def scans():
    analysis=None
    error=None
    filename=None
    scan_type=None
    if request.method=="POST":
        scan_type=request.form.get("scan_type")
        file=request.files.get("scan")
        if file is None:
            error="Please select a scan"
        elif file.filename=="":
            error="Please select a scan"
        else:
            filename=file.filename
            allowed_extensions=(".jpg","jpeg",".png")
            if not filename.lower().endswith(allowed_extensions):
                error=("currently supported formats are jpg, jpeg and png")
            elif not scan_type:
                error="Please select the type of scan"
            else:
                analysis=analyze_medical_scan(file,scan_type)
                if not analysis:
                    error=("the scan cannot be analyzed")
                else:
                    scan=Scan(user_id=current_user.id,scan_name=filename,scan_type=scan_type,analysis=analysis)
                    db.session.add(scan)
                    try:
                        db.session.commit()
                    except Exception as e:
                        db.session.rollback()
                        print("Scan database error:",e)
                        error="The scan analysis could not be saved"
    return render_template("scans.html",analysis=analysis, error=error, filename=filename, scan_type=scan_type)

@app.route("/trends")
@login_required
def trends():
    reports=db.session.query(Report).filter_by(user_id=current_user.id).order_by(Report.report_date.asc()).all()
    trends_data={}
    for report in reports:
        for value in report.values:
            if value.value is None:
                continue
            parameter=value.parameter.strip()
            if parameter not in trends_data:
                trends_data[parameter]={
                    "dates":[],
                    "values":[],
                    "units":[],
                    "reference_range":value.reference_range
                }
            trends_data[parameter]["dates"].append(report.report_date.strftime("%d %b %Y"))
            trends_data[parameter]["values"].append(value.value)
            trends_data[parameter]["units"].append(value.unit or "")
            if value.reference_range:
                trends_data[parameter]["refernce_range"]=value.reference_range
    for parameter,data in trends_data.items():
        values=data["values"]
        if len(values)<2:
            data["trend"]="Not enough data"
        else:
            first=values[0]
            latest=values[-1]
            if latest>first:
                data["trend"]="Increasing"
            elif latest<first:
                data["trend"]="Decreasing"
            else:
                data["trend"]="Stable"
        data["latest_value"]=values[-1]
        data["latest_unit"]=data["units"][-1] if data["units"] else ""
    return render_template("trends.html",trends_data=trends_data)

@app.route("/medicines",methods=["GET","POST"])
@login_required
def medicines():
    medicine_info=None
    medicine_name=None
    error=None
    if request.method=="POST":
        medicine_name=request.form.get("medicine","").strip()
        if not medicine_name:
            error="Please enter a medicine name"
        else:
            try:
                prompt=f"""
                You are providing general educational information about a medicine.
                Medicine: {medicine_name}
                Provide the information in this exact structure:
                ## What is it?
                Briefly explain what the medicine is.
                ## Common uses
                List common medical uses.
                ## How does it work?
                Give a simple explanation.
                ## Common side effects
                List commonly reported side effects.
                ## Important precautions
                Mention important precautions, interactions, allergies, pregnancy-related considerations,
                or conditions where professional advice is especially important.
                ## When to seek medical help
                Mention serious warning signs or situations requiring medical attention.
                Do NOT provide a personalized diagnosis or prescribe a dosage.
                Do NOT assume the user should take the medicine.
                Keep the response concise and easy to understand.
                """
                response=llm.invoke(prompt)
                medicine_info=response.content
                history_item = ChatHistory(user_id=current_user.id, query=f"Medicine: {medicine_name}",analysis=medicine_info)
                db.session.add(history_item)
                db.session.commit()
            except Exception as e:
                print("Info error",e)
                error=("Unable to retrieve info right now")
    return render_template("medicines.html",medicine_info=medicine_info,medicine_name=medicine_name,error=error)

@app.route("/profile",methods=["GET","POST"])
@login_required
def profile():
    profile_data=current_user.profile
    if request.method=="POST":
        age=request.form.get("age","").strip()
        gender=request.form.get("gender","").strip()
        if age:
            try:
                profile_data.age=int(age)
            except ValueError:
                flash("Age must be no","error")
                return render_template("profile.html", profile=profile_data)
        else:
            profile_data.age=None
        profile_data.gender=gender or None
        current_user.name=request.form.get("name",current_user.name).strip()
        db.session.commit()
        flash("Profile updated successfully","success")
        return redirect(url_for("profile"))
    return render_template("profile.html",profile=profile_data)

@app.route("/history")
@login_required
def history():
    chat_history=db.session.query(ChatHistory).filter_by(user_id=current_user.id).all()
    reports=db.session.query(Report).filter_by(user_id=current_user.id).all()
    scans=db.session.query(Scan).filter_by(user_id=current_user.id).all()
    activities=[]
    for item in chat_history:
        if item.query.startswith("Medicine:"):
            activities.append({"type": "medicine", "id": item.id, "title": item.query.replace("Medicine:", "").strip(), "content": item.analysis, "created_at": item.created_at})
        else:
            activities.append({"type":"research","id":item.id,"title":item.query,"content":item.analysis,"created_at":item.created_at})
    for report in reports:
        activities.append({"type":"report","id":report.id,"title":report.report_name,"content":report.analysis,"created_at":report.created_at})
    for scan in scans:
        activities.append({"type":"scan","id":scan.id,"title":scan.scan_name,"scan_type":scan.scan_type,"content":scan.analysis,"created_at":scan.created_at})
    activities.sort(key=lambda x: x["created_at"], reverse=True)

    return render_template("history.html",activities=activities)

@app.route("/about")
def about():
    return render_template("about.html")

if __name__=="__main__":
    app.run(debug=True)