import React, { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [page, setPage] = useState("home");
  const [result, setResult] = useState(null);
  const [resume, setResume] = useState(null);
  const [jobDesc, setJobDesc] = useState("");
  const [selectedRole, setSelectedRole] = useState("");
  const [loading, setLoading] = useState(false);

  // Result slideshow
  const [resultStep, setResultStep] = useState(0);

  const jobExamples = {
    "Python Developer":
      "We are looking for a Python Developer with experience in Python, Flask, Django, SQL, REST APIs, Git and Docker.",

    "AI/ML Engineer":
      "We are looking for an AI/ML Engineer with Python, machine learning, data analysis, SQL, TensorFlow or PyTorch and model development experience.",

    "Frontend Developer":
      "We are looking for a Frontend Developer with HTML, CSS, JavaScript, React, responsive design and Git experience.",

    "Backend Developer":
      "We are looking for a Backend Developer with Python, Java, Node.js, SQL, REST APIs, databases and Docker experience.",

    "Full Stack Developer":
      "We are looking for a Full Stack Developer with HTML, CSS, JavaScript, React, Node.js, SQL, REST APIs and Git experience.",

    "Data Analyst":
      "We are looking for a Data Analyst with Python, SQL, Excel, data analysis, visualization and statistics experience.",

    "Cloud Engineer":
      "We are looking for a Cloud Engineer with AWS, Azure, Docker, Kubernetes, Linux and cloud infrastructure experience.",

    "Cybersecurity Analyst":
      "We are looking for a Cybersecurity Analyst with networking, Linux, security monitoring, vulnerability assessment and incident response knowledge."
  };

  const floatingSkills = [
    { name: "Python", left: "9%", top: "19%", delay: "0s" },
    { name: "React", left: "72%", top: "18%", delay: "0.8s" },
    { name: "SQL", left: "80%", top: "40%", delay: "1.4s" },
    { name: "Flask", left: "8%", top: "48%", delay: "1.9s" },
    { name: "C++", left: "73%", top: "61%", delay: "0.5s" },
    { name: "AWS", left: "16%", top: "69%", delay: "1.2s" },
    { name: "JavaScript", left: "43%", top: "9%", delay: "2s" },
    { name: "Docker", left: "43%", top: "78%", delay: "0.7s" }
  ];

  const chooseRole = (role) => {
    setSelectedRole(role);
    setJobDesc(jobExamples[role]);
  };

  const analyzeResume = async () => {
    if (!resume) {
      alert("Please upload your resume PDF first.");
      return;
    }

    if (!jobDesc.trim()) {
      alert("Please select a target role or enter a job description.");
      return;
    }

    setLoading(true);
    setPage("scanning");

    try {
      const formData = new FormData();

      formData.append("resume", resume);
      formData.append("jobDesc", jobDesc);

      const response = await axios.post(
        "http://localhost:5000/analyze",
        formData
      );

      setResult(response.data);
      setResultStep(0);
      setPage("result");
    } catch (error) {
      console.error(error);

      alert(
        "Could not analyze the resume. Please make sure Python and Node are running."
      );

      setPage("upload");
    } finally {
      setLoading(false);
    }
  };

  const resetApp = () => {
    setPage("home");
    setResult(null);
    setResume(null);
    setJobDesc("");
    setSelectedRole("");
    setResultStep(0);
  };

  const nextStep = () => {
    if (resultStep < 3) {
      setResultStep(resultStep + 1);
    }
  };

  const previousStep = () => {
    if (resultStep > 0) {
      setResultStep(resultStep - 1);
    }
  };

  const score = result?.match_score || 0;
  const matchedSkills = result?.matched_skills || [];
  const missingSkills = result?.missing_skills || [];

  /* ------------------------------------------------ */
  /* HOME                                             */
  /* ------------------------------------------------ */

  if (page === "home") {
    return (
      <div className="app-shell">
        <nav className="top-nav">
          <div className="brand">CAREER SCANNER</div>

          <div className="nav-pill">AI CAREER DNA</div>
        </nav>

        <main className="home-screen">
          <div className="home-eyebrow">
            UNDERSTAND YOUR NEXT MOVE
          </div>

          <h1 className="home-title">
            Know Your
            <br />
            <span>Career DNA.</span>
          </h1>

          <p className="home-description">
            Discover how your current skills connect to the career
            you want next.
          </p>

          <button
            className="primary-button"
            onClick={() => setPage("upload")}
          >
            Enter Career Scanner →
          </button>

          <div className="home-orbit">
            <div className="home-orbit-dot dot-one"></div>
            <div className="home-orbit-dot dot-two"></div>
            <div className="home-orbit-dot dot-three"></div>
          </div>
        </main>
      </div>
    );
  }

  /* ------------------------------------------------ */
  /* UPLOAD                                           */
  /* ------------------------------------------------ */

  if (page === "upload") {
    return (
      <div className="app-shell">
        <nav className="top-nav">
          <div className="brand">CAREER SCANNER</div>

          <button
            className="secondary-button"
            onClick={() => setPage("home")}
          >
            ← Back
          </button>
        </nav>

        <main className="setup-screen">
          <div className="setup-header">
            <div className="step-label">STEP 01 — YOUR PROFILE</div>

            <h1>Build Your Career DNA</h1>

            <p>
              Start with your current resume, then tell us where
              you want to go.
            </p>
          </div>

          <div className="setup-card">
            <div className="upload-icon">📄</div>

            <h2>Upload your resume</h2>

            <p>PDF files are supported.</p>

            <input
              type="file"
              accept=".pdf"
              onChange={(event) => {
                setResume(event.target.files[0]);
              }}
            />

            {resume && (
              <div className="selected-file">
                ✓ {resume.name}
              </div>
            )}
          </div>

          <div className="target-section">
            <div className="step-label">
              STEP 02 — WHERE ARE YOU GOING?
            </div>

            <h2>Choose Your Target</h2>

            <p>
              Pick a common role or write your own job description.
            </p>

            <div className="role-grid">
              {Object.keys(jobExamples).map((role) => (
                <button
                  key={role}
                  className={
                    selectedRole === role
                      ? "role-button selected"
                      : "role-button"
                  }
                  onClick={() => chooseRole(role)}
                >
                  {role}
                </button>
              ))}
            </div>

            <textarea
              className="job-textarea"
              value={jobDesc}
              onChange={(event) => {
                setJobDesc(event.target.value);
                setSelectedRole("");
              }}
              placeholder="Or paste a job description here..."
            />

            <button
              className="primary-button"
              onClick={analyzeResume}
            >
              Scan My Future →
            </button>
          </div>
        </main>
      </div>
    );
  }

  /* ------------------------------------------------ */
  /* SCANNING                                         */
  /* ------------------------------------------------ */

  if (page === "scanning") {
    return (
      <div className="app-shell scanning-screen">
        <div className="scanner-orb">
          <div>🌐</div>
        </div>

        <div className="scanning-title">
          Mapping Your Career DNA
        </div>

        <div className="scanning-text">
          Comparing your profile with your target direction...
        </div>
      </div>
    );
  }

  /* ------------------------------------------------ */
  /* RESULT SLIDESHOW                                 */
  /* ------------------------------------------------ */

  if (page === "result" && result) {
    const targetName =
      selectedRole || "Your Target Role";

    return (
      <div className="result-shell">
        {/* TOP BAR */}

        <nav className="result-nav">
          <div className="brand">CAREER SCANNER</div>

          <div className="slide-counter">
            0{resultStep + 1} / 04
          </div>

          <button
            className="secondary-button"
            onClick={resetApp}
          >
            Start Again
          </button>
        </nav>

        {/* PROGRESS */}

        <div className="journey-progress">
          {[
            "PROFILE",
            "DISTANCE",
            "SKILL GAPS",
            "NEXT MOVE"
          ].map((label, index) => (
            <React.Fragment key={label}>
              <button
                className={
                  index === resultStep
                    ? "progress-item active"
                    : "progress-item"
                }
                onClick={() => setResultStep(index)}
              >
                <span>{index + 1}</span>
                {label}
              </button>

              {index < 3 && (
                <div
                  className={
                    index < resultStep
                      ? "progress-line filled"
                      : "progress-line"
                  }
                ></div>
              )}
            </React.Fragment>
          ))}
        </div>

        {/* SLIDES */}

        <div className="slides-window">
          <div
            className="slides-track"
            style={{
              transform: `translateX(-${resultStep * 25}%)`
            }}
          >
            {/* ------------------------------------ */}
            {/* SLIDE 1 — PROFILE                    */}
            {/* ------------------------------------ */}

            <section className="result-slide">
              <div className="slide-content">
                <div className="slide-eyebrow">
                  01 — YOUR PROFILE
                </div>

                <h1>Your Career DNA</h1>

                <p className="slide-description">
                  These are the skills currently detected in your
                  profile.
                </p>

                <div className="skill-galaxy">
                  {floatingSkills.map((skill) => {
                    const isMatched = matchedSkills.some(
                      (item) =>
                        item.toLowerCase() ===
                        skill.name.toLowerCase()
                    );

                    return (
                      <div
                        key={skill.name}
                        className={
                          isMatched
                            ? "floating-skill matched"
                            : "floating-skill"
                        }
                        style={{
                          left: skill.left,
                          top: skill.top,
                          animationDelay: skill.delay
                        }}
                      >
                        {skill.name}
                      </div>
                    );
                  })}

                  <div className="career-core">
                    <div className="core-icon">🌍</div>

                    <div className="core-small">
                      YOUR
                    </div>

                    <div className="core-title">
                      PROFILE
                    </div>
                  </div>
                </div>

                <div className="slide-bottom-text">
                  Your resume becomes the starting point of the
                  journey.
                </div>
              </div>
            </section>

            {/* ------------------------------------ */}
            {/* SLIDE 2 — DISTANCE                   */}
            {/* ------------------------------------ */}

            <section className="result-slide">
              <div className="slide-content compact">
                <div className="slide-eyebrow">
                  02 — CAREER DISTANCE
                </div>

                <h1>
                  How Close Are You?
                </h1>

                <div className="distance-layout">
                  <div className="score-circle">
                    <div className="score-number">
                      {score}%
                    </div>

                    <div className="score-label">
                      MATCH
                    </div>
                  </div>

                  <div className="distance-info">
                    <div className="path-box">
                      <div>
                        <span>YOUR PROFILE</span>
                        <strong>Current DNA</strong>
                      </div>

                      <div className="path-arrow">
                        →
                      </div>

                      <div>
                        <span>TARGET</span>
                        <strong>{targetName}</strong>
                      </div>
                    </div>

                    <p>
                      This score represents the proportion of
                      detected required skills that are present
                      in your resume.
                    </p>

                    <div className="score-bar">
                      <div
                        style={{
                          width: `${score}%`
                        }}
                      ></div>
                    </div>
                  </div>
                </div>

                <div className="calculation-note">
                  Based on detected required skills and matched
                  skills.
                </div>
              </div>
            </section>

            {/* ------------------------------------ */}
            {/* SLIDE 3 — SKILL GAPS                 */}
            {/* ------------------------------------ */}

            <section className="result-slide">
              <div className="slide-content compact">
                <div className="slide-eyebrow">
                  03 — SKILL GAPS
                </div>

                <h1>
                  What Separates You?
                </h1>

                <div className="gap-layout">
                  <div className="skill-column">
                    <div className="column-label">
                      ALREADY IN YOUR DNA
                    </div>

                    {matchedSkills.length === 0 ? (
                      <div className="empty-skill">
                        No direct matches detected.
                      </div>
                    ) : (
                      matchedSkills.map((skill) => (
                        <div
                          className="skill-row matched-row"
                          key={skill}
                        >
                          <span>✓</span>
                          {skill}
                        </div>
                      ))
                    )}
                  </div>

                  <div className="gap-divider">
                    →
                  </div>

                  <div className="skill-column">
                    <div className="column-label">
                      NEEDS ATTENTION
                    </div>

                    {missingSkills.length === 0 ? (
                      <div className="empty-skill positive">
                        No missing skills detected.
                      </div>
                    ) : (
                      missingSkills.map((skill) => (
                        <div
                          className="skill-row missing-row"
                          key={skill}
                        >
                          <span>○</span>
                          {skill}
                        </div>
                      ))
                    )}
                  </div>
                </div>
              </div>
            </section>

            {/* ------------------------------------ */}
            {/* SLIDE 4 — NEXT MOVE                 */}
            {/* ------------------------------------ */}

            <section className="result-slide">
              <div className="slide-content compact">
                <div className="slide-eyebrow">
                  04 — YOUR NEXT MOVE
                </div>

                <h1>
                  Turn Gaps Into Progress.
                </h1>

                {missingSkills.length === 0 ? (
                  <div className="next-message">
                    <div className="next-icon">✓</div>

                    <h2>
                      Your detected skills cover this target.
                    </h2>

                    <p>
                      Focus on demonstrating those skills through
                      projects, experience and stronger resume
                      evidence.
                    </p>
                  </div>
                ) : (
                  <div className="next-moves">
                    {missingSkills.slice(0, 5).map(
                      (skill, index) => (
                        <div
                          className="next-move-row"
                          key={skill}
                        >
                          <div className="move-number">
                            0{index + 1}
                          </div>

                          <div>
                            <strong>{skill}</strong>

                            <p>
                              Strengthen this skill for your
                              target role.
                            </p>
                          </div>

                          <div className="move-arrow">
                            →
                          </div>
                        </div>
                      )
                    )}
                  </div>
                )}

                <div className="target-final">
                  TARGET:
                  <strong>{targetName}</strong>
                </div>
              </div>
            </section>
          </div>
        </div>

        {/* NAVIGATION */}

        <div className="slide-navigation">
          <button
            className="slide-nav-button"
            onClick={previousStep}
            disabled={resultStep === 0}
          >
            ←
          </button>

          <div className="navigation-hint">
            {resultStep === 0 &&
              "Explore your current profile"}

            {resultStep === 1 &&
              "See your distance to the target"}

            {resultStep === 2 &&
              "Discover your skill gaps"}

            {resultStep === 3 &&
              "See what to work on next"}
          </div>

          <button
            className="slide-nav-button primary-nav"
            onClick={
              resultStep === 3
                ? resetApp
                : nextStep
            }
          >
            {resultStep === 3 ? "↻" : "→"}
          </button>
        </div>

        {/* PERSISTENT CAREER CORE */}

        <div className="persistent-core">
          <div className="core-ring"></div>

          <div className="persistent-core-icon">
            {resultStep === 0 && "🌍"}
            {resultStep === 1 && "🎯"}
            {resultStep === 2 && "🧩"}
            {resultStep === 3 && "🚀"}
          </div>

          <div className="persistent-core-label">
            {resultStep === 0 && "PROFILE"}
            {resultStep === 1 && "DISTANCE"}
            {resultStep === 2 && "GAPS"}
            {resultStep === 3 && "NEXT"}
          </div>
        </div>
      </div>
    );
  }

  return null;
}

export default App;