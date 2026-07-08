import SwiftUI

// MARK: - Auth chrome (RU / EN, same rules as `CompatibilityScreenChrome`)

private enum AuthScreenChrome {
    static var useRussian: Bool {
        if let code = Locale.current.language.languageCode?.identifier.lowercased() {
            if code == "ru" { return true }
            if code == "en" { return false }
        }
        return Bundle.main.preferredLocalizations.first?.lowercased().hasPrefix("ru") == true
    }

    static var segmentSignIn: String { useRussian ? "Вход" : "Sign in" }
    static var segmentSignUp: String { useRussian ? "Регистрация" : "Create account" }
    static var pickerMode: String { useRussian ? "Режим" : "Mode" }

    static var emailTitle: String { useRussian ? "Эл. почта" : "Email" }
    static var emailCaption: String {
        useRussian
            ? "Этот адрес станет постоянным идентификатором аккаунта."
            : "This email becomes your persistent account identity."
    }
    static var passwordTitle: String { useRussian ? "Пароль" : "Password" }
    static func passwordCaptionSignIn() -> String {
        useRussian ? "Минимум 8 символов." : "Minimum 8 characters."
    }

    static func passwordCaptionSignUp() -> String {
        useRussian
            ? "Не меньше 8 символов. Лучше не повторять слабый пароль."
            : "Use at least 8 characters. Avoid reusing a weak password."
    }

    static var confirmPasswordTitle: String { useRussian ? "Пароль ещё раз" : "Confirm password" }
    static var confirmPasswordCaption: String {
        useRussian ? "Введи тот же пароль, без отличий." : "Repeat the same password exactly."
    }

    static var forgotPassword: String { useRussian ? "Забыли пароль?" : "Forgot password" }
    static var needAccount: String { useRussian ? "Нужен аккаунт?" : "Need an account?" }
    static var alreadyRegistered: String { useRussian ? "Уже есть аккаунт?" : "Already registered?" }

    static var valEmailEmpty: String { useRussian ? "Введи email." : "Enter your email." }
    static var valEmailInvalid: String { useRussian ? "Введи корректный email." : "Enter a valid email address." }
    static var valPasswordEmpty: String { useRussian ? "Введи пароль." : "Enter your password." }
    static var valPasswordShort: String {
        useRussian ? "Пароль — не меньше 8 символов." : "Password must contain at least 8 characters."
    }
    static var valConfirmEmpty: String { useRussian ? "Подтверди пароль." : "Confirm your password." }
    static var valPasswordsMismatch: String { useRussian ? "Пароли не совпадают." : "Passwords do not match." }

    static var heroBrand: String { "TODAYFLOW" }
    static var heroTitle: String {
        useRussian ? "Единый вход в персональный контур" : "One sign-in for your personal layer"
    }

    static var heroBody: String {
        useRussian
            ? "Сессия сохраняется на устройстве. После входа продолжаешь путь без потери прогресса."
            : "Your session stays on this device. After sign-in you continue without losing progress."
    }

    static var heroChipSession: String { useRussian ? "Сессия сохраняется" : "Session stays on device" }
    static func heroChipMode(_ signIn: Bool) -> String {
        if useRussian {
            return signIn ? "Быстрый вход" : "Регистрация и запуск"
        }
        return signIn ? "Quick sign-in" : "Register and start"
    }

    static var heroChipRecovery: String { useRussian ? "Восстановление пароля" : "Password recovery" }

    static func modeTitle(_ mode: AuthView.Mode) -> String {
        switch mode {
        case .signIn: return useRussian ? "Вход в TodayFlow" : "Sign in to TodayFlow"
        case .signUp: return useRussian ? "Создать аккаунт" : "Create account"
        }
    }

    static func modeSubtitle(_ mode: AuthView.Mode) -> String {
        switch mode {
        case .signIn:
            return useRussian
                ? "Войди и продолжай с последнего шага без повторного онбординга."
                : "Sign in and pick up where you left off—no onboarding repeat."
        case .signUp:
            return useRussian
                ? "Один аккаунт для Сегодня, Flow, Guidance, Совместимости и Профиля."
                : "One account for Today, Flow, Guidance, Compatibility, and Profile."
        }
    }

    static func modeSubmit(_ mode: AuthView.Mode) -> String {
        switch mode {
        case .signIn: return useRussian ? "Войти" : "Sign in"
        case .signUp: return useRussian ? "Создать аккаунт" : "Create account"
        }
    }

    // Password recovery sheet
    enum Recovery {
        static var pickerAction: String { AuthScreenChrome.useRussian ? "Действие" : "Action" }
        static var segmentRequest: String { AuthScreenChrome.useRussian ? "Письмо со ссылкой" : "Send reset email" }
        static var segmentReset: String { AuthScreenChrome.useRussian ? "Токен и новый пароль" : "Enter reset token" }

        static var subtitleRequest: String {
            AuthScreenChrome.useRussian
                ? "Запроси письмо со сбросом на этот аккаунт."
                : "Ask the backend to generate a reset email for this account."
        }

        static var subtitleReset: String {
            AuthScreenChrome.useRussian
                ? "Вставь токен из письма и задай новый пароль."
                : "Paste the token you received, then set a new password."
        }

        static var sectionAccount: String { AuthScreenChrome.useRussian ? "Аккаунт" : "Account" }
        static var sectionToken: String { AuthScreenChrome.useRussian ? "Токен сброса" : "Reset token" }
        static var tokenPlaceholder: String { AuthScreenChrome.useRussian ? "Вставь токен" : "Paste token" }
        static var sectionNewPassword: String { AuthScreenChrome.useRussian ? "Новый пароль" : "New password" }
        static var newPasswordPlaceholder: String { AuthScreenChrome.useRussian ? "Новый пароль" : "New password" }
        static var confirmNewPlaceholder: String { AuthScreenChrome.useRussian ? "Повтор нового пароля" : "Confirm new password" }

        static var navTitle: String { AuthScreenChrome.useRussian ? "Доступ по паролю" : "Password access" }
        static var close: String { AuthScreenChrome.useRussian ? "Закрыть" : "Close" }
        static var sendEmail: String { AuthScreenChrome.useRussian ? "Отправить письмо" : "Send reset email" }
        static var resetPassword: String { AuthScreenChrome.useRussian ? "Сбросить пароль" : "Reset password" }

        static var valEmailEmpty: String {
            AuthScreenChrome.useRussian ? "Введи email этого аккаунта." : "Enter the email used for this account."
        }

        static var valEmailInvalid: String {
            AuthScreenChrome.useRussian ? "Введи корректный email." : "Enter a valid email address."
        }

        static var valTokenEmpty: String { AuthScreenChrome.useRussian ? "Вставь токен сброса." : "Paste the reset token." }
        static var valNewShort: String {
            AuthScreenChrome.useRussian
                ? "Новый пароль — не меньше 8 символов."
                : "New password must contain at least 8 characters."
        }

        static var valConfirmEmpty: String {
            AuthScreenChrome.useRussian ? "Подтверди новый пароль." : "Confirm the new password."
        }

        static var valPasswordsMismatch: String {
            AuthScreenChrome.useRussian ? "Пароли не совпадают." : "Passwords do not match."
        }
    }
}

struct AuthView: View {
    enum Mode: String, CaseIterable, Identifiable {
        case signIn
        case signUp

        var id: String { rawValue }
    }

    let store: TodayFlowStore

    @State private var mode: Mode = .signIn
    @State private var email = ""
    @State private var password = ""
    @State private var confirmPassword = ""
    @State private var isPasswordVisible = false
    @State private var isConfirmPasswordVisible = false
    @State private var isSubmitting = false
    @State private var feedbackMessage: String?
    @State private var isRecoveryPresented = false

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 24) {
                    AuthHero(mode: mode)

                    VStack(alignment: .leading, spacing: 20) {
                        Picker(AuthScreenChrome.pickerMode, selection: $mode) {
                            Text(AuthScreenChrome.segmentSignIn).tag(Mode.signIn)
                            Text(AuthScreenChrome.segmentSignUp).tag(Mode.signUp)
                        }
                        .pickerStyle(.segmented)

                        VStack(alignment: .leading, spacing: 8) {
                            Text(AuthScreenChrome.modeTitle(mode))
                                .font(.title2.weight(.semibold))
                                .foregroundStyle(TodayFlowTheme.ink)

                            Text(AuthScreenChrome.modeSubtitle(mode))
                                .font(.subheadline)
                                .foregroundStyle(TodayFlowTheme.ink.opacity(0.74))
                        }

                        VStack(alignment: .leading, spacing: 14) {
                            AuthInputGroup(
                                title: AuthScreenChrome.emailTitle,
                                caption: AuthScreenChrome.emailCaption
                            ) {
                                emailField("name@example.com", text: $email)
                            }

                            AuthInputGroup(
                                title: AuthScreenChrome.passwordTitle,
                                caption: mode == .signIn ? AuthScreenChrome.passwordCaptionSignIn() : AuthScreenChrome.passwordCaptionSignUp()
                            ) {
                                PasswordField(
                                    title: AuthScreenChrome.passwordTitle,
                                    text: $password,
                                    isVisible: $isPasswordVisible
                                )
                            }

                            if mode == .signUp {
                                AuthInputGroup(
                                    title: AuthScreenChrome.confirmPasswordTitle,
                                    caption: AuthScreenChrome.confirmPasswordCaption
                                ) {
                                    PasswordField(
                                        title: AuthScreenChrome.confirmPasswordTitle,
                                        text: $confirmPassword,
                                        isVisible: $isConfirmPasswordVisible
                                    )
                                }
                            }
                        }

                        if let validationMessage {
                            AuthMessageRow(
                                text: validationMessage,
                                tint: .orange,
                                icon: "exclamationmark.circle"
                            )
                        } else if let feedbackMessage {
                            AuthMessageRow(
                                text: feedbackMessage,
                                tint: .secondary,
                                icon: "info.circle"
                            )
                        }

                        Button(action: submit) {
                            HStack(spacing: 10) {
                                if isSubmitting {
                                    ProgressView()
                                        .tint(.white)
                                }
                                Text(AuthScreenChrome.modeSubmit(mode))
                                    .font(.headline)
                            }
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 14)
                        }
                        .buttonStyle(.borderedProminent)
                        .tint(TodayFlowTheme.accent)
                        .disabled(validationMessage != nil || isSubmitting)

                        HStack {
                            Button(AuthScreenChrome.forgotPassword) {
                                isRecoveryPresented = true
                            }
                            .buttonStyle(.plain)
                            .foregroundStyle(TodayFlowTheme.accent)

                            Spacer()

                            Button(mode == .signIn ? AuthScreenChrome.needAccount : AuthScreenChrome.alreadyRegistered) {
                                withAnimation(.snappy) {
                                    mode = mode == .signIn ? .signUp : .signIn
                                }
                            }
                            .buttonStyle(.plain)
                            .foregroundStyle(.secondary)
                        }
                    }
                    .padding(24)
                    .background(TodayFlowTheme.card)
                    .clipShape(RoundedRectangle(cornerRadius: 28, style: .continuous))
                }
                .todayFlowContentContainer(maxWidth: 780, horizontal: 20, top: 10, bottom: 14)
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .background(TodayBackground())
            .sheet(isPresented: $isRecoveryPresented) {
                PasswordRecoveryView(store: store)
            }
        }
        .onChange(of: mode) { _, _ in
            clearMessages()
        }
        .onChange(of: email) { _, _ in
            feedbackMessage = nil
        }
        .onChange(of: password) { _, _ in
            feedbackMessage = nil
        }
        .onChange(of: confirmPassword) { _, _ in
            feedbackMessage = nil
        }
    }

    private var cleanEmail: String {
        String(
            email.unicodeScalars.filter {
                !CharacterSet.whitespacesAndNewlines.contains($0) &&
                !CharacterSet.controlCharacters.contains($0)
            }
        )
            .lowercased()
    }

    private var cleanPassword: String {
        String(
            password.unicodeScalars.filter {
                !CharacterSet.newlines.contains($0) &&
                !CharacterSet.controlCharacters.contains($0)
            }
        )
            .trimmingCharacters(in: .whitespacesAndNewlines)
    }

    private var validationMessage: String? {
        if cleanEmail.isEmpty {
            return AuthScreenChrome.valEmailEmpty
        }
        if !cleanEmail.isPlausibleEmail {
            return AuthScreenChrome.valEmailInvalid
        }
        if cleanPassword.isEmpty {
            return AuthScreenChrome.valPasswordEmpty
        }
        if cleanPassword.count < 8 {
            return AuthScreenChrome.valPasswordShort
        }
        if mode == .signUp && confirmPassword.isEmpty {
            return AuthScreenChrome.valConfirmEmpty
        }
        if mode == .signUp && cleanPassword != confirmPassword.trimmingCharacters(in: .whitespacesAndNewlines) {
            return AuthScreenChrome.valPasswordsMismatch
        }
        return nil
    }

    private func submit() {
        guard validationMessage == nil else { return }
        feedbackMessage = nil
        isSubmitting = true

        Task {
            do {
                switch mode {
                case .signIn:
                    try await store.signIn(email: cleanEmail, password: cleanPassword)
                case .signUp:
                    try await store.signUp(email: cleanEmail, password: cleanPassword)
                }

                await MainActor.run {
                    isSubmitting = false
                    password = ""
                    confirmPassword = ""
                }
            } catch {
                await MainActor.run {
                    isSubmitting = false
                    feedbackMessage = error.localizedDescription
                }
            }
        }
    }

    private func clearMessages() {
        feedbackMessage = nil
        password = ""
        confirmPassword = ""
    }
}

private struct AuthHero: View {
    let mode: AuthView.Mode

    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            Text(AuthScreenChrome.heroBrand)
                .font(.caption.weight(.semibold))
                .foregroundStyle(.secondary)

            Text(AuthScreenChrome.heroTitle)
                .font(.system(size: 34, weight: .bold, design: .rounded))
                .foregroundStyle(TodayFlowTheme.ink)

            Text(AuthScreenChrome.heroBody)
                .font(.subheadline)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.82))

            HStack(spacing: 12) {
                AuthFeatureChip(text: AuthScreenChrome.heroChipSession, systemImage: "checkmark.shield")
                AuthFeatureChip(
                    text: AuthScreenChrome.heroChipMode(mode == .signIn),
                    systemImage: mode == .signIn ? "arrow.uturn.forward.circle" : "person.badge.plus"
                )
                AuthFeatureChip(text: AuthScreenChrome.heroChipRecovery, systemImage: "key")
            }
        }
        .padding(28)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(.ultraThinMaterial)
        .clipShape(RoundedRectangle(cornerRadius: 32, style: .continuous))
    }
}

private struct AuthInputGroup<Content: View>: View {
    let title: String
    let caption: String
    @ViewBuilder let content: Content

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title)
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.ink)

            content

            Text(caption)
                .font(.caption)
                .foregroundStyle(.secondary)
        }
    }
}

private struct AuthFeatureChip: View {
    let text: String
    let systemImage: String

    var body: some View {
        Label(text, systemImage: systemImage)
            .font(.caption.weight(.medium))
            .padding(.horizontal, 12)
            .padding(.vertical, 8)
            .background(Color.white.opacity(0.72))
            .clipShape(Capsule())
    }
}

private struct PasswordField: View {
    let title: String
    @Binding var text: String
    @Binding var isVisible: Bool

    var body: some View {
        HStack(spacing: 10) {
            Group {
                if isVisible {
                    TextField(title, text: $text)
                        .todayFlowSecureInput()
                } else {
                    SecureField(title, text: $text)
                        .todayFlowSecureInput()
                }
            }

            Button {
                isVisible.toggle()
            } label: {
                Image(systemName: isVisible ? "eye.slash" : "eye")
                    .foregroundStyle(.secondary)
            }
            .buttonStyle(.plain)
        }
    }
}

private struct AuthMessageRow: View {
    let text: String
    let tint: Color
    let icon: String

    var body: some View {
        HStack(alignment: .top, spacing: 10) {
            Image(systemName: icon)
                .foregroundStyle(tint)

            Text(text)
                .font(.footnote)
                .foregroundStyle(.secondary)
        }
        .padding(14)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(tint.opacity(0.08))
        .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
    }
}

private struct PasswordRecoveryView: View {
    enum RecoveryMode: String, CaseIterable, Identifiable {
        case request
        case reset

        var id: String { rawValue }

        var subtitle: String {
            switch self {
            case .request: return AuthScreenChrome.Recovery.subtitleRequest
            case .reset: return AuthScreenChrome.Recovery.subtitleReset
            }
        }
    }

    let store: TodayFlowStore

    @Environment(\.dismiss) private var dismiss
    @State private var mode: RecoveryMode = .request
    @State private var email = ""
    @State private var token = ""
    @State private var newPassword = ""
    @State private var confirmPassword = ""
    @State private var isSubmitting = false
    @State private var message: String?

    var body: some View {
        NavigationStack {
            Form {
                Section {
                    Picker(AuthScreenChrome.Recovery.pickerAction, selection: $mode) {
                        Text(AuthScreenChrome.Recovery.segmentRequest).tag(RecoveryMode.request)
                        Text(AuthScreenChrome.Recovery.segmentReset).tag(RecoveryMode.reset)
                    }

                    Text(mode.subtitle)
                        .font(.footnote)
                        .foregroundStyle(.secondary)
                }

                if mode == .request {
                    Section(AuthScreenChrome.Recovery.sectionAccount) {
                        emailField("name@example.com", text: $email)
                    }
                } else {
                    Section(AuthScreenChrome.Recovery.sectionToken) {
                        TextField(AuthScreenChrome.Recovery.tokenPlaceholder, text: $token)
                            .todayFlowPlainTextInput()
                    }

                    Section(AuthScreenChrome.Recovery.sectionNewPassword) {
                        SecureField(AuthScreenChrome.Recovery.newPasswordPlaceholder, text: $newPassword)
                            .todayFlowSecureInput()

                        SecureField(AuthScreenChrome.Recovery.confirmNewPlaceholder, text: $confirmPassword)
                            .todayFlowSecureInput()
                    }
                }

                if let validationMessage {
                    Section {
                        AuthMessageRow(
                            text: validationMessage,
                            tint: .orange,
                            icon: "exclamationmark.circle"
                        )
                    }
                } else if let message {
                    Section {
                        AuthMessageRow(
                            text: message,
                            tint: .secondary,
                            icon: "checkmark.circle"
                        )
                    }
                }

                Section {
                    Button(mode == .request ? AuthScreenChrome.Recovery.sendEmail : AuthScreenChrome.Recovery.resetPassword) {
                        submit()
                    }
                    .disabled(isSubmitting || validationMessage != nil)
                }
            }
            .navigationTitle(AuthScreenChrome.Recovery.navTitle)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button(AuthScreenChrome.Recovery.close) {
                        dismiss()
                    }
                }
            }
        }
        .onChange(of: mode) { _, _ in
            message = nil
            token = ""
            newPassword = ""
            confirmPassword = ""
        }
    }

    private var validationMessage: String? {
        switch mode {
        case .request:
            let cleanEmail = email.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
            if cleanEmail.isEmpty {
                return AuthScreenChrome.Recovery.valEmailEmpty
            }
            if !cleanEmail.isPlausibleEmail {
                return AuthScreenChrome.Recovery.valEmailInvalid
            }
            return nil

        case .reset:
            if token.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
                return AuthScreenChrome.Recovery.valTokenEmpty
            }
            if newPassword.trimmingCharacters(in: .whitespacesAndNewlines).count < 8 {
                return AuthScreenChrome.Recovery.valNewShort
            }
            if confirmPassword.isEmpty {
                return AuthScreenChrome.Recovery.valConfirmEmpty
            }
            if newPassword.trimmingCharacters(in: .whitespacesAndNewlines) != confirmPassword.trimmingCharacters(in: .whitespacesAndNewlines) {
                return AuthScreenChrome.Recovery.valPasswordsMismatch
            }
            return nil
        }
    }

    private func submit() {
        guard validationMessage == nil else { return }
        isSubmitting = true
        message = nil

        Task {
            do {
                let result: String
                switch mode {
                case .request:
                    result = try await store.requestPasswordReset(
                        email: email.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
                    )
                case .reset:
                    result = try await store.resetPassword(
                        token: token.trimmingCharacters(in: .whitespacesAndNewlines),
                        newPassword: newPassword.trimmingCharacters(in: .whitespacesAndNewlines)
                    )
                }

                await MainActor.run {
                    isSubmitting = false
                    message = result
                    if mode == .reset {
                        token = ""
                        newPassword = ""
                        confirmPassword = ""
                    }
                }
            } catch {
                await MainActor.run {
                    isSubmitting = false
                    message = error.localizedDescription
                }
            }
        }
    }
}

@ViewBuilder
private func emailField(_ title: String, text: Binding<String>) -> some View {
    TextField(title, text: text)
        .todayFlowEmailInput()
        .textFieldStyle(RoundedBorderTextFieldStyle())
}

private extension String {
    var isPlausibleEmail: Bool {
        let trimmed = trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty, !trimmed.contains(" ") else { return false }
        let parts = trimmed.split(separator: "@")
        guard parts.count == 2, !parts[0].isEmpty, parts[1].contains(".") else { return false }
        return true
    }
}

extension View {
    @ViewBuilder
    func todayFlowEmailInput() -> some View {
#if os(iOS)
        textInputAutocapitalization(.never)
            .autocorrectionDisabled()
            .keyboardType(.emailAddress)
            .keyboardType(.asciiCapable)
            .textContentType(.username)
#else
        self
#endif
    }

    @ViewBuilder
    func todayFlowPlainTextInput() -> some View {
#if os(iOS)
        textInputAutocapitalization(.never)
            .autocorrectionDisabled()
            .keyboardType(.asciiCapable)
#else
        self
#endif
    }

    @ViewBuilder
    func todayFlowSecureInput() -> some View {
        self
            .textFieldStyle(RoundedBorderTextFieldStyle())
#if os(iOS)
            .textInputAutocapitalization(.never)
            .autocorrectionDisabled()
            .keyboardType(.asciiCapable)
            .textContentType(.password)
#endif
    }

    @ViewBuilder
    func todayFlowSystemTextInput(words: Bool = false) -> some View {
#if os(iOS)
        if words {
            textInputAutocapitalization(.words)
                .keyboardType(.default)
                .textContentType(.none)
        } else {
            textInputAutocapitalization(.sentences)
                .keyboardType(.default)
                .textContentType(.none)
        }
#else
        self
#endif
    }

    @ViewBuilder
    func todayFlowCodeInput() -> some View {
#if os(iOS)
        textInputAutocapitalization(.never)
            .autocorrectionDisabled()
            .keyboardType(.asciiCapable)
#else
        self
#endif
    }
}
